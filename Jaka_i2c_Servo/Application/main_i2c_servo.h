#ifndef _main_i2c_servo_h_
#define _main_i2c_servo_h_

/*----------------------------------------------------------------------------*/
/*  Include public headers                                                    */
/*----------------------------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
/* definitions from etype.h                                                   */
/*----------------------------------------------------------------------------*/
#ifndef TRUE
  #define TRUE (1)
#endif 
#ifndef FALSE
  #define FALSE (0)
#endif 

#ifndef bool
  #define bool unsigned char
#endif 

#ifndef UINT8
  #define UINT8 unsigned char
#endif 

#ifndef INT16
  #define INT16 int
#endif 

#ifndef UINT16
  #define UINT16 unsigned int
#endif 

#ifndef BITMASK16
  #define BITMASK16 unsigned int
#endif 

#ifndef UINT32
  #define UINT32 unsigned long
#endif 

#ifndef INT32
  #define INT32 long
#endif 

/*----------------------------------------------------------------------------*/
/* Logical trigger flags and macros                                           */
/*----------------------------------------------------------------------------*/
#ifndef TRUE
  #define TRUE true
#endif 
#ifndef FALSE
  #define FALSE false
#endif 


struct S_TRIGGER {
  bool Curr; 
  bool Prev;
};
typedef struct S_TRIGGER T_TRIGGER;

struct S_TRIGGER8 {
  UINT8 Curr; 
  UINT8 Prev;
};
typedef struct S_TRIGGER8 T_TRIGGER8;

struct S_TRIGGER32 {
  UINT32 Curr; 
  UINT32 Prev;
};
typedef struct S_TRIGGER32 T_TRIGGER32;

// Macros work with pointers to trig
#define TRIG_INIT(Hnd) (Hnd)->Curr=FALSE; (Hnd)->Prev=FALSE; 
// Writes Val to Curr value
#define TRIG_WR(Hnd,Val) (Hnd)->Curr=(Val);
// Writes TRUE to Curr
#define TRIG_SET(Hnd) TRIG_WR(Hnd,TRUE)
// Writes FALSE to Curr
#define TRIG_RESET(Hnd) TRIG_WR(Hnd,FALSE)
// Increments current
#define TRIG_INC(Hnd) (Hnd)->Curr++;
#define TRIG_DEC(Hnd) (Hnd)->Curr--;

// returns pointer to Curr
#define TRIG_CURR(Hnd) (Hnd)->Curr
// Returns curr value

#define TRIG_GET_CURR(Hnd) (Hnd)->Curr
#define TRIG_GET(Hnd) TRIG_GET_CURR(Hnd)
#define TRIG_GET_PREV(Hnd) (Hnd)->Prev

// Copies Curr to Prev. Now there are no events
#define TRIG_COPY(Hnd) (Hnd)->Prev=(Hnd)->Curr;
// Any change?
#define TRIG_IS(Hnd) ((Hnd)->Prev!=(Hnd)->Curr)
#define TRIG_IS_RISING(Hnd) (!(Hnd)->Prev && (Hnd)->Curr)
#define TRIG_IS_FALLING(Hnd) ((Hnd)->Prev && !(Hnd)->Curr)
// Both Prev and Curr elements have value Val
#define TRIG_IS_FULL(Hnd,Val) (((Hnd)->Prev==Val) && ((Hnd)->Curr==Val))

/*----------------------------------------------------------------------------*/
/* Support for bits                                                           */
/*----------------------------------------------------------------------------*/
#define BIT_SET(Val,Mask)   Val|=Mask;
#define BIT_RESET(Val,Mask) Val&=(~Mask);
#define BIT_WR(Val,Mask)    Val=Mask;


/*----------------------------------------------------------------------------*/
/* Support for limits                                                         */
/*----------------------------------------------------------------------------*/
#ifndef min
  #define min(a,b) ((a)<(b))?(a):(b)
#endif

#ifndef max
  #define max(a,b) ((a)<(b))?(b):(a)
#endif

#define MIN_OF(a,b)  (min(a,b))
#define MAX_OF(a,b)  (max(a,b))

#define SET_IN_LIMITS_OF(a,low,high)  MAX_OF((MIN_OF((a),(high))),(low))
#define IS_IN_LIMITS_INCLUSIVE(a,low,high)  (((a)>=(low)) && ((a)<=(high)))

// Round x to multiple of y
#define ROUNDDOWN(x,y)  (((x)/(y))*(y))
#define ROUNDUP(x,y)    ((((x)+(y)-1)/(y))*(y))

/*----------------------------------------------------------------------------*/
/* Support for simple Simple SW timer                                         */
/*----------------------------------------------------------------------------*/
#define TIMER_START(Timer,Timeout) Timer=Timeout;
#define TIMER_STOP(Timer) Timer=0;
// must be callse periodic to make timer run
#define TIMER_MOVE(Timer) if (Timer) Timer--;
#define TIMER_IS_RUNNING(Timer) (Timer>0)
#define TIMER_IS_EXPIRED(Timer) (Timer<=0)

/*----------------------------------------------------------------------------*/
/* Own definitions                                                            */
/*----------------------------------------------------------------------------*/

#ifdef __cplusplus
extern "C" {
#endif

/*----------------------------------------------------------------------------*/
/* Constants                                                                  */
/*----------------------------------------------------------------------------*/  
#define I2C_SERVO_ADDR 0x20  // Motor drive slave adress

/*----------------------------------------------------------------------------*/
/* Configuration                                                              */
/*----------------------------------------------------------------------------*/
#define NO_SERVOS     (2) //number of servos
#define I2C_CMD_IS_PARAM_MASK      (0x80) // Other 7 bits are parameter
#define I2C_CMD_SERVO_NO_MASK         (0x40) // 1=servo 2, 0 - servo 1
#define I2C_CMD_ON_MASK            (0x20) // Must be 1 to drive
#define I2C_CMD_DIR_LEFT_MASK      (0x10) // 1 to drive left
#define I2C_CMD_SERVO_ANGLE_MASK   (0x0F) // 16 steps for each direction

/*----------------------------------------------------------------------------*/
/* Timing parameters                                                          */
/*----------------------------------------------------------------------------*/  
#define SAMPLING_RATE_US     (180) //interupt timer constant 1000==1ms

#define SERVO_MIDDLE         (180) // 1,5ms
#define SERVO_STEP_RESOL       (5) // 1,5ms
#define SERVO_MIN             (80) //((int)(SERVO_MIDDLE+100)) // 1 ms
#define SERVO_MAX            (280) //((int)(SERVO_MIDDLE-100)) // 1 ms


// Max time in ticks between consecutive i2c commands to stop motors  
#define I2C_CMD_TIMEOUT   (300) // ms   
    
/* functional mapping **************************************/
#define SERVO1_OUT_PORT            P1OUT
#define SERVO1_OUT_MASK            BIT4
#define SERVO2_OUT_PORT            P1OUT
#define SERVO2_OUT_MASK            BIT5

#define MAIN_ON_OUT_PORT          P1OUT 
#define MAIN_ON_OUT_MASK          BIT1

/* I2C interface */
#define I2C_SCL_MASK              BIT6
#define I2C_SDA_MASK              BIT7

/* testing */
#define IN_TEST_BUTTON_PORT       P1IN
#define IN_TEST_BUTTON_MASK       BIT1
    
#define ALL_P1_OUT (SERVO1_OUT_MASK|SERVO2_OUT_MASK|MAIN_ON_OUT_MASK) 
/*----------------------------------------------------------------------------*/
/* I2C FSM                                                                    */
/*----------------------------------------------------------------------------*/
typedef enum{
  I2C_WAIT_CMD =   0, // Accepting command
  I2C_WAIT_PARAM = 1 // Accepting parameter block
} i2c_state_type;

/*----------------------------------------------------------------------------*/
/* Public functions                                                           */
/*----------------------------------------------------------------------------*/

#ifdef __cplusplus
}
#endif
#endif /* _main_i2c_servo_h_ */
/*----------------------------------------------------------------------------*/
/*  End of module                                                             */
/*----------------------------------------------------------------------------*/
