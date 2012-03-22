//#include  <msp430x20x2.h>
// Must minimize code footprint to very minimum, we have only few bytes left
// Works much better on CCS, but takes more code

#include <msp430g2231.h>
#include "main_i2c_servo.h"
#include "USI_I2CSlave.h"

// BP 2.1.11 i2c related forwards, from example_slave430interface.c 
int i2c_RxCallback(unsigned char);
int i2c_TxCallback(int*);
void i2c_StartCallback();

volatile UINT8 CurrI2cState; // = I2C_WAIT_CMD;
volatile UINT8 PrevI2cState; // = I2C_WAIT_CMD;
T_TRIGGER8 i2cRxCmdCounter;// = {0,0}; // increments i2c callback, when new command has arrived
                                   // Accepts Timer irq
volatile int i2cCmdsTimer;// = 0;      // Counts timer ticks between i2c commands. If no command issue stop

volatile unsigned char Activei2cCmd = 0; // Last active command from i2c

volatile unsigned char i2cCmd; //=0;  // Last active command from i2c



/* functions */
void initPhase(void);
/* transient functions */
void checkI2C(void);

unsigned int CmdReg;
UINT8 StatusReg=0; // Motor status to Trol_Chair

// Working variables for 
unsigned int counter = 0;                   // Servo counter
unsigned int servoPosition[NO_SERVOS] = {SERVO_MIDDLE,SERVO_MIDDLE};
unsigned int demoCounter = 0;                   // Demo move counter insted of i2c

void main(void)
{
  WDTCTL = WDTPW+WDTHOLD;                   // disable Watchdog
  
  if (CALBC1_1MHZ ==0xFF || CALDCO_1MHZ == 0xFF)                                     
  {  
    while(1);                               // If calibration constants erased                                            // do not load, trap CPU!!
  }   
  BCSCTL1 = CALBC1_1MHZ;                    // Set DCO
  BCSCTL1 &= ~XT2OFF;
  _BIS_SR(OSCOFF);
  P2SEL &= ~0x80;       // Activate Port function on P2.7  
  DCOCTL = CALDCO_1MHZ;

// setup P1 outputs
  P1OUT &= ~(ALL_P1_OUT);          // We could replace those BITs with define or simply 0xF0, but I left it for clarity
  P1DIR |=  (ALL_P1_OUT);           // Port P1.4-1.7 is out
  P1SEL &= ~(ALL_P1_OUT);

  /* Initialize USI module in Slave mode */      
  TI_USI_I2C_SlaveInit(I2C_SERVO_ADDR,i2c_StartCallback,i2c_RxCallback,i2c_TxCallback);  
  // Wait 1s before start

  //interupt timer init
  CCTL0 = CCIE;                             // CCR0 interrupt enabled
  CCR0 = SAMPLING_RATE_US;                  
  TACTL = TASSEL_2 + MC_1 + ID_3;           // SMCLK/8, upmode
  //TACTL = TASSEL_2 + MC_1;           // SMCLK/8, upmode

  _bis_SR_register(LPM0_bits + GIE);        // Enter LPM0 w/ interrupt

  // never get here
  while (1);
}

// Timer A0 interrupt service routine
#pragma vector=TIMERA0_VECTOR
__interrupt void Timer_A (void)
{ 
  int ServoToSet; 
  checkI2C(); // Get new commands from i2c
#if 0  
// DEMO movement overrides i2c
  demoCounter++;
  if(demoCounter == 4000)  Activei2cCmd = I2C_CMD_ON_MASK+I2C_CMD_DIR_LEFT_MASK+0;
  if(demoCounter == 8000) Activei2cCmd = I2C_CMD_ON_MASK+15;
  if(demoCounter == 12000) Activei2cCmd = I2C_CMD_ON_MASK+I2C_CMD_DIR_LEFT_MASK+15;
//  if(demoCounter == 2400) Activei2cCmd = I2C_CMD_DIR_LEFT_MASK+10;
  if(demoCounter == 12000) 
  {
//    Activei2cCmd = I2C_CMD_ON_MASK+I2C_CMD_DIR_LEFT_MASK+0;
    demoCounter = 0;
  }
 // END DEMO movement
#endif

// Parse command from i2c
  ServoToSet = (Activei2cCmd & I2C_CMD_SERVO_NO_MASK)?1:0; 
  // First servo position
  if (Activei2cCmd & I2C_CMD_DIR_LEFT_MASK)
  {
    servoPosition[ServoToSet] = SERVO_MIDDLE + SERVO_STEP_RESOL*(Activei2cCmd&I2C_CMD_SERVO_ANGLE_MASK);    
  }
  else
  {
    servoPosition[ServoToSet] = SERVO_MIDDLE - SERVO_STEP_RESOL*(Activei2cCmd&I2C_CMD_SERVO_ANGLE_MASK);    
  }
 
  // Main on/off
  if (Activei2cCmd & I2C_CMD_ON_MASK)
  {
    BIT_SET(MAIN_ON_OUT_PORT,MAIN_ON_OUT_MASK);    
  }
  else
  {
    BIT_RESET(MAIN_ON_OUT_PORT,MAIN_ON_OUT_MASK);
    // if off, set servo to middle
    servoPosition[0] = SERVO_MIDDLE;        
    servoPosition[1] = SERVO_MIN;        
  }
  // Limit servo position to sane values
  servoPosition[ServoToSet] = SET_IN_LIMITS_OF(servoPosition[ServoToSet],SERVO_MIN,SERVO_MAX);
  //servoPosition = SET_IN_LIMITS_OF(servoPosition,(80),(280));
        
// Prepare timing for servo  
  counter++;
  if (counter==(NO_SERVOS+1)) counter = 0;
  
  BIT_RESET(SERVO1_OUT_PORT,SERVO1_OUT_MASK);
  BIT_RESET(SERVO2_OUT_PORT,SERVO2_OUT_MASK);
  if (counter==NO_SERVOS)
  {
    CCR0 = 1500;      // ~10ms delay    
//    CCR0 = servoPosition; // Time for next interrupt    

  }
  else
  {
    switch (counter) {
      case 0:
        BIT_SET(SERVO1_OUT_PORT,SERVO1_OUT_MASK);
        CCR0 = servoPosition[0]; // Time for next interrupt    
        break;
      case 1:
        BIT_SET(SERVO2_OUT_PORT,SERVO2_OUT_MASK);
        CCR0 = servoPosition[1]; // Time for next interrupt    
        break;
      default:
    } // switch
  }
  
}

#if 0
bool checkLocalButtons(void){ 
#ifdef SIMUL_SHORT_CIRCUIT
  return FALSE; // no local buttons  
#else  
  if (MAN_UP_PORT & IN_MAN_UP_MASK)
  {
    currentTransientCondition = GO_TO_LEFT_STATE;
    return TRUE;
  }
  if (MAN_UP_PORT & IN_MAN_DN_MASK)
  {
    currentTransientCondition = GO_TO_RIGHT_STATE;
    return TRUE;
  }    
//  currentTransientCondition=GO_TO_STOP_STATE;      
  return FALSE;
#endif // SIMUL_SHORT_CIRCUIT  
}
#endif

void checkI2C(void)
{      
  // Move timer
  TIMER_MOVE(i2cCmdsTimer);
  // Check command from i2c
  if (TRIG_IS(&i2cRxCmdCounter))
  {   
    TIMER_START(i2cCmdsTimer,I2C_CMD_TIMEOUT);
    Activei2cCmd = i2cCmd;

  }
  TRIG_COPY(&i2cRxCmdCounter);
#if 1
  // Add timer control to stop motor without commands  
  if (TIMER_IS_EXPIRED(i2cCmdsTimer))
  {
    Activei2cCmd=0;    
  }
#endif  
}

void i2c_StartCallback()
{
// BP Debug with LA    
  P1OUT |= 0x01;                              // start received, turn LED on 
  CurrI2cState = I2C_WAIT_CMD; // any receive must start at I2C_WAIT_CMD
// BP Debug with LA    
  P1OUT &= ~0x01;                      
  
}

int i2c_RxCallback(unsigned char RxData)
{  
// BP Debug with LA  P1OUT &= ~0x01;                      
  switch(CurrI2cState){
      case I2C_WAIT_CMD :
        i2cCmd = RxData;
#if 0
        if (RxData & I2C_CMD_PARAMS_MSK)
        {          
          i2cParamCounter=RxData & I2C_PARAMS_SIZE_MSK;
          i2cParamIdx = 0;
          i2cParamCounter = MIN_OF(i2cParamCounter,ALL_PARAMETERS_SIZE);
          if (i2cParamCounter>0)
          {
            CurrI2cState = I2C_WAIT_PARAM;                        
          }
          else
          {
            CurrI2cState = I2C_WAIT_CMD;
// BP Debug with LA              P1OUT &= ~0x01;                      
          }
        }
        else
        {
          CurrI2cState = I2C_WAIT_CMD;
          // BP Debug with LA            P1OUT &= ~0x01;          
        }          
#endif
        TRIG_INC(&i2cRxCmdCounter);        
        break;        
  default:
    CurrI2cState = I2C_WAIT_CMD;    
  } // switch()


//  i2cFSM(RxData); 
  return TI_USI_STAY_LPM ;                  // stay in LPM
}

int i2c_TxCallback(int* TxDataPtr)
{
//   MotorSetStatus();
   *(UINT8*)TxDataPtr = StatusReg;
//   TxDataPtr = (int*)&i2cStatusReg;
   
  // Data byte to be transmitted is passed through reference to the library
// *(unsigned char*)TxDataPtr = *(unsigned char*)ptr_tx;
//  ptr_tx++;                                 // Increment tx pointer
  return TI_USI_STAY_LPM ;                  // stay in LPM
}

// eof


