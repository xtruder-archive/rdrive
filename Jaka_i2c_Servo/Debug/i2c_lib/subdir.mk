################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
ASM_SRCS += \
../i2c_lib/USI_I2CSlave.asm 

ASM_DEPS += \
./i2c_lib/USI_I2CSlave.pp 

OBJS += \
./i2c_lib/USI_I2CSlave.obj 

OBJS__QTD += \
".\i2c_lib\USI_I2CSlave.obj" 

ASM_DEPS__QTD += \
".\i2c_lib\USI_I2CSlave.pp" 

ASM_SRCS_QUOTED += \
"../i2c_lib/USI_I2CSlave.asm" 


# Each subdirectory must supply rules for building sources it contributes
i2c_lib/USI_I2CSlave.obj: ../i2c_lib/USI_I2CSlave.asm $(GEN_OPTS)
	@echo 'Building file: $<'
	@echo 'Invoking: Compiler'
	"C:/Program Files/Texas Instruments/ccsv4/tools/compiler/msp430/bin/cl430" --silicon_version=msp -g --include_path="C:/Program Files/Texas Instruments/ccsv4/msp430/include" --include_path="C:/Projekti/TROL/TROL/Jaka_i2c_Servo/i2c_lib" --include_path="C:/Program Files/Texas Instruments/ccsv4/tools/compiler/msp430/include" --diag_warning=225 --printf_support=minimal --preproc_with_compile --preproc_dependency="i2c_lib/USI_I2CSlave.pp" --obj_directory="i2c_lib" $(GEN_OPTS_QUOTED) $(subst #,$(wildcard $(subst $(SPACE),\$(SPACE),$<)),"#")
	@echo 'Finished building: $<'
	@echo ' '


