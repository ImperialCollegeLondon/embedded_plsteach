#include "mbed.h"
#include "../Crypto/Crypto.h"
#include <string>
#include <stdio.h>

//Photointerrupter input pins
#define I1pin D3
#define I2pin D6
#define I3pin D5

//Incremental encoder input pins
#define CHApin   D12
#define CHBpin   D11

//Motor Drive output pins   //Mask in output byte
#define L1Lpin D1           //0x01
#define L1Hpin A3           //0x02
#define L2Lpin D0           //0x04
#define L2Hpin A6          //0x08
#define L3Lpin D10           //0x10
#define L3Hpin D2          //0x20

#define PWMpin D9

//Motor current sense
#define MCSPpin   A1
#define MCSNpin   A0

#define R_MAX 0
#define V_MAX 0

#define KS_P 25.0
#define KS_I 0.11
#define KR_P 29.7
#define KR_D 252.0

#define MAX_DUTYCL 1000
#define PWM_PERIOD 2000

//Mapping from sequential drive states to motor phase outputs
/*
State   L1  L2  L3
0       H   -   L
1       -   H   L
2       L   H   -
3       L   -   H
4       -   L   H
5       H   L   -
6       -   -   -
7       -   -   -
*/
//Drive state to output table
const int8_t driveTable[] = {0x12,0x18,0x09,0x21,0x24,0x06,0x00,0x00};

//Mapping from interrupter inputs to sequential rotor states. 0x00 and 0x07 are not valid
const int8_t stateMap[] = {0x07,0x05,0x03,0x04,0x01,0x00,0x02,0x07};  

//Phase lead to make motor spin
int8_t lead = 2;  //2 for forwards, -2 for backwards

//Status LED
DigitalOut led1(LED1);

//Photointerrupter inputs
InterruptIn I1(I1pin);
InterruptIn I2(I2pin);
InterruptIn I3(I3pin);

PwmOut Pwm(D9);

AnalogIn C0(A0);
AnalogIn C1(A1);

//Motor Drive outputs
DigitalOut L1L(L1Lpin);
DigitalOut L1H(L1Hpin);
DigitalOut L2L(L2Lpin);
DigitalOut L2H(L2Hpin);
DigitalOut L3L(L3Lpin);
DigitalOut L3H(L3Hpin);

typedef struct {
  int8_t type;
  float content;
} mail_msg;

enum msgCode {
    motorPosition,
    motorVelocity,
    newPos,
    newVel,
    nce,
    hashRate,
    showTorque,
    er = 255    
    };

int8_t orState = 0;
volatile int32_t motorPos = 0; //in states
volatile int32_t old_motorPos = 0; //in states
volatile float tar_Velocity = 10; //in revs per second
volatile float tar_Rotation = 0; //in revs
volatile int32_t motorDty = 7000; // /10000 -> 0.7

RawSerial pc(SERIAL_TX, SERIAL_RX);

Mail<mail_msg, 16> out_mail;
Queue<void, 8> in_comm;

Mutex key;

//Set a given drive state
void motorOut(int8_t driveState, int32_t cycle){
    float pulsewidth = cycle/10000;
    
    //Lookup the output byte from the drive state.
    int8_t driveOut = driveTable[driveState & 0x07];
      
    //Turn off first
    if (~driveOut & 0x01) L1L = 0;
    if (~driveOut & 0x02) L1H = 1;
    if (~driveOut & 0x04) L2L = 0;
    if (~driveOut & 0x08) L2H = 1;
    if (~driveOut & 0x10) L3L = 0;
    if (~driveOut & 0x20) L3H = 1;
    
    //Then turn on
    if (driveOut & 0x01) L1L = 1;
    if (driveOut & 0x02) L1H = 0;
    if (driveOut & 0x04) L2L = 1;
    if (driveOut & 0x08) L2H = 0;
    if (driveOut & 0x10) L3L = 1;
    if (driveOut & 0x20) L3H = 0;
    
    Pwm.write(0.5f);
    } 
    
    //Convert photointerrupter inputs to a rotor state
inline int8_t readRotorState(){
    return stateMap[I1 + 2*I2 + 4*I3];
    }
 
int8_t motorHome() {
    motorOut(0, motorDty);
    wait(2.0);
    return readRotorState();
    }
    
void putMsg(int8_t type, float content) { //put msg in mail for outSerial
        mail_msg *msg = out_mail.alloc();
        msg->type = type;
        msg->content = content;
        out_mail.put(msg);
    }
void motorISR(){
    static int8_t oldState;
    int8_t rotorState = readRotorState();
    
    motorOut((rotorState-orState+lead+6)%6, motorDty);
    
    int8_t stateDiff = rotorState - oldState;
    if (stateDiff == -5)
        motorPos ++;
    else if (stateDiff == +5)
        motorPos--;
    else
        motorPos += stateDiff;
    oldState = rotorState;
    }

Thread motorCtrlT(osPriorityNormal, 1024);    
void motorCtrlTick(){
    motorCtrlT.signal_set(0x1); 
    }

void motorController() {
  Ticker motorCtrlTicker;
  Timer t;
  motorCtrlTicker.attach_us(&motorCtrlTick, 100000);
  float velocity = 0.0;
  int32_t currPos = 0;

  float error_s;
  int32_t T_s;
  static float error_s_int = 0;

  float error_r;
  int32_t T_r;
  static float error_r_int = 0;
  static float old_error_r;

  int32_t ctorque = 0;
  uint8_t iterations = 0;
  while (1) {
    //t.start();
    motorCtrlT.signal_wait(0x1);
    
    core_util_critical_section_enter();
    currPos = motorPos;
    core_util_critical_section_exit();
    
    //t.stop();
    velocity = (currPos - old_motorPos) * 10;
    old_motorPos = currPos;
    //t.reset();
    iterations++;
    if (iterations%20==0) {
      putMsg(motorPosition, old_motorPos);
      putMsg(motorVelocity, velocity);
      putMsg(showTorque, motorDty);
      iterations = 0;
    }

    error_s = (tar_Velocity * 6.0f - abs(velocity));
    T_s = (int)(KS_P * error_s);
    //T_s = (int32_t)(KS_P * error_s + KS_I * error_s_int);
    error_s_int += error_s;

    /*error_r = tar_Rotation - currPos / 6.0f;
    T_r = (int32_t)(KR_P * error_r + KR_D * (error_r - old_error_r));
    old_error_r = error_r;
    error_r_int += error_r;

    if (error_r < 0) 
        T_s = -T_s;

    if ((error_r > -0.4) && (error_r < 0.4)) 
        T_r = 0;

    if (velocity >= 0){
      if (T_s < T_r){
        ctorque = T_s;
        error_r_int = 0;
      } else {
        ctorque = T_r;
        error_s_int = 0;
      }
    } else {
        if (T_s > T_r){
          ctorque = T_s;
          error_r_int = 0;
        } else {
          ctorque = T_r;
          error_s_int = 0;
        }
    }*/
    ctorque = T_s;
   
    if (ctorque < 0) {
      ctorque = -ctorque;
      lead = -2;
    }else{
      lead = 2;  
        }

    if (ctorque > MAX_DUTYCL)
        motorDty = MAX_DUTYCL;
    else
      motorDty = ctorque;
      
    if (velocity == 0)
        motorISR();
  }
}
    
void outSerialThread(){
    while(1){
        osEvent evt = out_mail.get();
        if (evt.status == osEventMail) {
            mail_msg *msg = (mail_msg*)evt.value.p;
            switch(msg->type){
                
                case motorPosition:
                    pc.printf("Current position is %d\n\r", (int32_t)msg->content);
                    break;
                    
                case motorVelocity:
                    pc.printf("Current velocity is %.2f\n\r", msg->content);
                    break;
                
                case newPos:
                    pc.printf("New target rotation is %d\n\r", (int32_t)msg->content);
                    break;
                
                case newVel:
                    pc.printf("New target velocity is %.2f\n\r", msg->content);
                    break;
                
                case showTorque:
                    pc.printf("motor duty cycle is: %d\n\r", (int32_t)msg->content);
                    break;
                    
                case nce:
                    pc.printf("nonce\t:\t%X\n\r", (uint32_t)msg->content); 
                    break;
                
                case hashRate:
                    pc.printf("Hash rate :\t%d\n\r", (int32_t)msg->content);
                    break;
                    
                case er:
                    pc.printf("Unknown error\n\r");
                
                default:
                    pc.printf("Unmatched message type with content: %d\n\r", (int32_t)msg->content);
                    break;
                }
            out_mail.free(msg);
            }
        }
    }

void inSerialISR(){  // Incoming communication ISR
    uint8_t newChar = pc.getc();
    in_comm.put((void*)newChar);
    }

void parser(char* input){
    float value_in = 0;
    char type = input[0];
    switch(type){
        case 'R':
            //for rotation command
            //R-?\d{1,3}(\.\d{1,2})?
            //eg. R101.21
            sscanf(input, "R%f", &value_in);
            if (value_in>0){
                tar_Rotation += value_in;
                putMsg(newPos, tar_Rotation);   
            }else{
                tar_Rotation = R_MAX;
                putMsg(newPos, tar_Rotation);
            }
            break;
        case 'V':
            //for maximum speed command
            //V\d{1,3}(\.\d)?
            //V0 = spin as fast as possible
            sscanf(input, "V%f", &value_in);
            if (value_in>0){
                tar_Velocity = value_in;
                putMsg(newVel, tar_Velocity);
            }else{
                tar_Velocity = V_MAX;
                putMsg(newVel, tar_Velocity);
            }
            break;
        case 'K':
            //for setting bitcoin key
            //K[0-9a-fA-F]{16}
            //sscanf(input, "K%16x", &value_in);
            //output = value_in;
            break;
        //case 'T':
//            //for melody commands
//            //T([A-G][#^]?[1-8]){1,16}
//            //# and ^ are characters
//            //eg. TGab34
//            sscanf(input, "T[A-G][%c%c]?[1-8]", &value_in);
//            output = value_in;
        default:
            putMsg(er,2);
        }
    }

void decoderThread(){ // Decoder thread
    pc.attach(&inSerialISR);
    static int char_counter = 0;
    char cmd[30];
    while(1){
        osEvent trigger = in_comm.get();
        uint8_t newChar = (uint8_t)trigger.value.p;
        if (char_counter>=30){
            char_counter = 0;
            putMsg(er, 0x1);
        }else{
                if (newChar != '\r'){
                cmd[char_counter] = newChar;
                char_counter++;
                }
            else{
                cmd[char_counter] = '\0';
                char_counter = 0;
                parser(cmd);
                }     
            }
        }
    }


int main() {

    pc.printf("Motor @PlzTeach");
    Pwm.period_us(PWM_PERIOD);
    Thread inComms; 
    Thread outComms; //output thread
    Thread controller(osPriorityHigh, 1024);
    
    inComms.start(&decoderThread);
    outComms.start(&outSerialThread);
    controller.start(&motorController);
    motorCtrlT.start(motorController);
    
    orState = motorHome();
    
    I1.rise(&motorISR);
    I1.fall(&motorISR);
    I2.rise(&motorISR);
    I2.fall(&motorISR);
    I3.rise(&motorISR);
    I3.fall(&motorISR);
    
    pc.printf("Waiting command");
    
    Timer t;
    t.start();
    int hashcounter = 0;
    SHA256 bithash = SHA256();
    uint8_t sequence[] = {  0x45,0x6D,0x62,0x65,0x64,0x64,0x65,0x64,
                            0x20,0x53,0x79,0x73,0x74,0x65,0x6D,0x73,
                            0x20,0x61,0x72,0x65,0x20,0x66,0x75,0x6E,
                            0x20,0x61,0x6E,0x64,0x20,0x64,0x6F,0x20,
                            0x61,0x77,0x65,0x73,0x6F,0x6D,0x65,0x20,
                            0x74,0x68,0x69,0x6E,0x67,0x73,0x21,0x20,
                            0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                            0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
    uint64_t* key = (uint64_t*)((int)sequence + 48);
    uint64_t* nonce = (uint64_t*)((int)sequence + 56);
    uint8_t hash[32];
    
    while(1){
        //compute hash using bitcoin lib 
        bithash.SHA256::computeHash(hash, sequence, 64);
        
        //we want to find a nonce value where it gives hash[0] and hash[1] == 0
      if((hash[0] == 0x00) && (hash[1] == 0x00)){        
      
        //this is the nonce we want
          putMsg(nce, *nonce);
      }
      
        //we want to print out hashes per second
        //if time >= 1 we reset it, and we count how many hashes are there in a second 
      if(t.read() >= 1){
          t.stop();
          putMsg(hashRate, hashcounter);
          hashcounter = 0;
          t.reset();
          t.start();
          }
      (*nonce)++;
      hashcounter++;;
        }
}

