################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Application/main_i2c_servo.c 

OBJS += \
./Application/main_i2c_servo.obj 

C_DEPS += \
./Application/main_i2c_servo.pp 

OBJS__QTD += \
".\Application\main_i2c_servo.obj" 

C_DEPS__QTD += \
".\Application\main_i2c_servo.pp" 

C_SRCS_QUOTED += \
"../Application/main_i2c_servo.c" 


# Each subdirectory must supply rules for building sources it contributes
Application/main_i2c_servo.obj: ../Application/main_i2c_servo.c $(GEN_OPTS)
	@echo 'Building file: $<'
	@echo 'Invoking: Compiler'
	"C:/Program Files/Texas Instruments/ccsv4/tools/compiler/msp430/bin/cl430" --silicon_version=msp -g --include_path="C:/Program Files/Texas Instruments/ccsv4/msp430/include" --include_path="C:/Projekti/TROL/TROL/Jaka_i2c_Servo/i2c_lib" --include_path="C:/Program Files/Texas Instruments/ccsv4/tools/compiler/msp430/include" --diag_warning=225 --printf_support=minimal --preproc_with_compile --preproc_dependency="Application/main_i2c_servo.pp" --obj_directory="Application" $(GEN_OPTS_QUOTED) $(subst #,$(wildcard $(subst $(SPACE),\$(SPACE),$<)),"#")
	@echo 'Finished building: $<'
	@echo ' '


