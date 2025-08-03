/*
  ## brutzelboy-dumper ##
  UPDATE: This code was changed to be compatible for ESP32-S3 / arduin nano and a custom PCB
  -> for https://github.com/theBrutzler/ESP32_GBC_RETROFIT // for "thebrutzler adapter for brutzelboy "
  type: gb+gbc
  Version: 0.5e
  Author: WodoWiesel
  github: (https://github.com/wodowiesel/GB-Dumper)
  Last Modified: 28. May 2025
*/
//------
// import library
#include <Wire.h> // i2c
// https://github.com/adafruit/Adafruit_AW9523/blob/master/Adafruit_AW9523.cpp
// https://learn.adafruit.com/adafruit-aw9523-gpio-expander-and-led-driver/pinouts
// https://adafruit.github.io/Adafruit_AW9523/html/class_adafruit___a_w9523.html#abc6f9bf84927de2740a5727e7cbb9353 commands
#include <Adafruit_AW9523.h> // i2c expander
//--------------
// Digital Pins-> D-Numbers
// aw_1
#define GB_A0 0
#define GB_A1 1
#define GB_A2 2
#define GB_A3 3
#define GB_A4 4 // sda
#define GB_A5 5 // clk
#define GB_A6 6
#define GB_A7 7
#define GB_A8 8
#define GB_A9 9
#define GB_A10 10
#define GB_A11 11
#define GB_A12 12
#define GB_A13 13
#define GB_A14 14
#define GB_A15 15

// aw_2
#define GB_D0 0
#define GB_D1 1
#define GB_D2 2
#define GB_D3 3
#define GB_D4 4
#define GB_D5 5
#define GB_D6 6
#define GB_D7 7
#define GB_CLK 8 //output
#define GB_WR 9 // output
#define GB_RD 10 // output
#define GB_CS 11 // output
#define GB_RES 12 // output CS2 for GBA 
#define GB_VIN 13 // output AUDIO GB & IRQ for GBA 
#define GB_VOLT 14 // output switch 5 & 3V3 
//---------
#define BAUD 115200
#define SDA 2 // Ard_A4
#define SCL 1 // Ard_A5

//--------
// expander activation
#define EX1 0x58
#define EX2 0x5A
Adafruit_AW9523 aw_1; // addr 0x58
Adafruit_AW9523 aw_2; //addr 0x5A
//-------------
// define variables
//uint32_t BAUD = 115200;  // max speed, for serial connection with minimal error rate 19200
// https://gbdev.io/pandocs/Power_Up_Sequence.html

char r;
char readInput[10];
uint8_t readCount = 0;

char gsl2 = 0;
char gsl1 = 0;

uint8_t nintendoLogo[] = {
  0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B, 0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
  0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E, 0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
  0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC, 0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E
}; // 48 byte
uint8_t logoCheck = 1;
uint16_t x = 0;

char gameTitle[17]; // max 4(instr)+12 (name) byte or 16 name-> depends on game and region
char manufTitle[6];

uint8_t cgbflag = 0x00;
uint8_t sgbflag = 0x00;

uint8_t cartridgeType = 0x00;
uint8_t romSize = 0x00;
uint8_t romBanks = 2; // assumed Default 32K, 2 banks a KB
uint32_t romEndAddress = 0x0000;

uint8_t ramSize = 0x00;
uint8_t ramBanks = 0; // Default 0K RAM
uint32_t ramEndAddress = 0x01FFFF; // 128 KB

uint16_t region = 0x0000;

uint8_t licensee = 0x00;
uint8_t licensee_new = 0x00;

uint8_t romver = 0x00;

uint16_t headercs = 0x0000;
uint8_t hcheck = 0x00;
uint8_t z = 0;
//uint8_t h = 0;
//uint16_t p[25]; // 0x0134
uint8_t hcs = 0;

uint32_t calculated_global_checksum = 0x0000;
uint8_t gcs = 0;

uint8_t readData[64];

//--- setup start & connections
void setup() {
  //--------- init connection
  Serial.begin(BAUD);  // for 4/16 MHz clock , -> SERIAL_8N1 standard
  delay(10); // wait for bootup

  // https://github.com/arduino/ArduinoCore-megaavr/blob/master/libraries/Wire/src/utility/twi.c#L179
  // Formula is: BAUD = ((F_CLKPER/frequency) - F_CLKPER*T_RISE - 10)/2;
  Wire.setClock(100000); // clockFrequency , 100000 (standard),(200K double rate) 400k fastmode
  //Wire.begin(SDA, SCL); // esp32-s3 brutzi SDA, SCL
  Wire.begin(); // nano slave addr 42 -> 0x2A, sda pin 18 A4, 19 scl A5// gbc I2C bus ->esp: address, scl, sda, *buffer, len

  //-------- setup i2c
  if(Wire.available() <= 0) { // peripheral may send less than requested
    delay(100);
    //-----------------
  }
  else {
    //Serial.print("I2C available");
    //delay(10);
  
    if (!aw_1.begin(EX1)) { //dec 88
      Serial.println("AW9523_1 not found? Check wiring!");
      Serial.flush();
      while (1) {delay(10);}  // halt forever
    }

    if (!aw_2.begin(EX2)) { // dec 90
      Serial.println("AW9523_2 not found? Check wiring!");
      Serial.flush();
      while(1) {delay(10);}  // halt forever
    }
  }

  for(uint8_t address = 0; address <= 15; address++) {
    aw_1.pinMode(address, OUTPUT); // A0-A15
    aw_1.digitalWrite(address, HIGH);
  }

  for(uint8_t address = 0; address <= 7; address++) {
    aw_2.pinMode(address, INPUT); // D0-D7 sure its input?
    aw_2.digitalWrite(address, HIGH);
  }

  aw_2.pinMode(GB_CLK, OUTPUT); // 8 clock active
  aw_2.digitalWrite(GB_CLK, HIGH);

  for(uint8_t address = 9; address <= 11; address++) { // old 15
    aw_2.pinMode(address, OUTPUT); // WR-CS active
    aw_2.digitalWrite(address, LOW);
  }

  aw_2.pinMode(GB_RES, OUTPUT); // 12 reset deactivated (active low)
  aw_2.digitalWrite(GB_RES, HIGH);
  
  aw_2.pinMode(GB_VIN, OUTPUT); // 13 output esp-> card input audio!
  aw_2.digitalWrite(GB_VIN, HIGH);
  //aw_2.interruptEnableGPIO(GB_VIN); // IRQ für GBA
  //aw_2.enableInterrupt(GB_VIN); // IRQ für GBA
  
  aw_2.pinMode(GB_VOLT, OUTPUT); // 14
  aw_2.digitalWrite(GB_VOLT, HIGH); // high 5v & low 3v3 maybe?

  // Sets direction for all 16 GPIO, 1 == output, 0 == input.
  //aw_1.configureDirection(1);
  //aw_2.configureDirection(1);
  
  rd_wr_mreq_off();

}
//-- loop  menu start

void loop() {

  // Wait for serial input
  while(Serial.available() <= 0) {
    delay(10);
  }

  while(Serial.available() > 0) {
    // Decode input
    r = Serial.read(); // maybe parameters idk
    readInput[readCount] = r;
    readCount++;
  }
  readInput[readCount] = '\0';
  //----

  // first menu option
  // Cartridge Header
  if(strstr(readInput, "HEADER")) {
    rd_wr_mreq_reset(); // reset status

    // --------------
    // last 2 bytes describes adress
    gsl2 = (char) read_byte(0x0103);
    Serial.println(gsl2);

    gsl1 = (char) read_byte(0x0102);
    Serial.println(gsl1); // print serial to py script for header info readout

    //-------
    // Nintendo Logo Check
    // https://stackoverflow.com/questions/21119904/how-to-decode-the-nintendo-logo-from-gameboyssss

    for(uint32_t romAddress = 0x0104; romAddress <= 0x0133; romAddress++) { 
      if(nintendoLogo[x] != read_byte(romAddress)) {
        logoCheck = 0;
        break;
      }
      x++;
    }
    Serial.println(logoCheck);
    //----------
    // Read cartridge title and check for non-printable text
    for(uint32_t romAddress = 0x0134; romAddress <= 0x0143; romAddress++) {
      char headerChar = (char) read_byte(romAddress);
      // https://www.rapidtables.com/code/text/ascii-table.html
      if(((headerChar >= 0x20) && (headerChar <= 0x7E))  ||  // space (0x20) or ! x21 to ~
          ((headerChar >= 0x80) && (headerChar <= 0xFF)) ) { // extended special chars
        gameTitle[(romAddress - 0x0134)] = headerChar; // only read/printable characters
       }

    }

    gameTitle[16] = '\0'; // terminate the title for finish with escape
    Serial.println(gameTitle);

    //------------
    //Manufacturer Code

    for(uint32_t romAddress = 0x013F; romAddress <= 0x0142; romAddress++) {
      char manufChar = (char) read_byte(romAddress);
      // https://www.rapidtables.com/code/text/ascii-table.html
      if(((manufChar >= 0x20) && (manufChar <= 0x7E))  ||  // space to ~
          ((manufChar >= 0x80) && (manufChar <= 0xFF)) ) { // extended special chars
        manufTitle[(romAddress - 0x013F)] = manufChar; // only read/printable characters
      }

    }

    manufTitle[6] = '\0'; // terminate the title for finish with escape
    Serial.println(manufTitle);
    //----------
    cgbflag = read_byte(0x0143); // dec: 323
    Serial.println(cgbflag); // if 1 / true -> save rom as gbc, 0 as gb

    //----------
    // test if super gb
    sgbflag = read_byte(0x0146); // dec: 326
    Serial.println(sgbflag);

    //----------
    // check cartridge type, romtype, ram, battery, mbc, rumble, multi, cmera, rtc, arp, voice
    cartridgeType = read_byte(0x0147); // dec:327 / MBC type should be specified in the byte at 0147hex of the ROM
    Serial.println(cartridgeType);

    //----------
    // read romsize & banks
    romSize = read_byte(0x0148); // dec: 328
    Serial.println(romSize);

    if(romSize == 0x00) { // $0000-$3FFF: ROM Bank $00 (Read Only) first 16KB of the cartridge, the first memory bank. It is unable to be switched or modified.
      romBanks = 1;
    }
    else if(romSize >= 0x01) { // Calculate rom banks
      romBanks = (2 << romSize);
    }
    else { // None or 0 banks
      romBanks = 0;
    }
    Serial.println(romBanks);
//----------------
    uint32_t rom_size_full = 0; // unused atm
    if(romSize == 0x00) { // not used atm
      rom_size_full = 32767;    // 32 KB
      romEndAddress = 0x7FFF; // =(banks*16*1024)-1
    }
    else if(romSize == 0x01) {
      rom_size_full = 65535;    // 64 KB
      romEndAddress = 0xFFFF;
    }
    else if(romSize == 0x02) {
      rom_size_full = 131071;    // 128 KB
      romEndAddress = 0x1FFFF;
    }
    else if(romSize == 0x03) {
      rom_size_full = 262143;    // 256 KB
      romEndAddress = 0x3FFFF;
    }
    else if(romSize == 0x04) {
      rom_size_full = 524287;    // 512 KB
      romEndAddress = 0x7FFFF;
    }
    else if(romSize == 0x05 && ((cartridgeType == 0x01) || (cartridgeType == 0x02) || (cartridgeType == 0x03))) {
      rom_size_full = 1032191;  // 1008 KByte (63 banks)
      romEndAddress = 0xFBFFF;
    }
    else if(romSize == 0x05) {
      rom_size_full = 1048575;   // 1 MB
      romEndAddress = 0xFFFFF;
    }
    else if(romSize == 0x06 && ((cartridgeType == 0x01) || (cartridgeType == 0x02) || (cartridgeType == 0x03))) {
      rom_size_full = 2047999;  // 2 MByte (125 banks)
      romEndAddress = 0x1F3FFF;
    }
    else if(romSize == 0x06) {
      rom_size_full = 2097151;   // 2 MB 128 banks
      romEndAddress = 0x1FFFFF;
    }
    else if(romSize == 0x07) {
      rom_size_full = 4194303;   // 4 MB
      romEndAddress = 0x3FFFFF;
    }
    else if(romSize == 0x08) {
      rom_size_full = 8388607;  // 8 MB max
      romEndAddress = 0x7FFFFF;
    }
    else if(romSize == 0x0D) {
      rom_size_full = 262143;   // 256 KB
      romEndAddress = 0x03FFFF;
    }
    else if(romSize == 0x52) {
      rom_size_full = 1179647;   // 1.1 MB
      romEndAddress = 0x11FFFF;
    }
    else if(romSize == 0x53) {
      rom_size_full = 1310719;   // 1.2 MB
      romEndAddress = 0x13FFFF;
    }
    else if(romSize == 0x54) {
      rom_size_full = 1572863;   // 1.5 MB
      romEndAddress = 0x17FFFF;
    }
    else if(romSize == 0xFF) {
      rom_size_full = 32767;   // 32 KB
      romEndAddress = 0x7FFF;
    }
    else {
      rom_size_full = 0x00; // Return 0 for unknown size
      romEndAddress = 0x0000;
    } 
    //Serial.println(rom_size_full);
    Serial.println(romEndAddress, HEX);

    //----------
    // read ram size
    ramSize = read_byte(0x0149); // dec: 329
    Serial.println(ramSize);

    // RAM banks

    if(ramSize == 0x00) {
      ramBanks = 0;
    }
    else if((ramSize == 0x00) && (cartridgeType == 0x06)) {
      ramBanks = 1;
    }
    else if(ramSize == 0x01) {
      ramBanks = 1;
    }
    else if(ramSize == 0x02) {
      ramBanks = 1;
    }
    else if(ramSize == 0x03) {
      ramBanks = 4;
    }
    else if(ramSize == 0x04) {
      ramBanks = 16;
    }
    else if(ramSize == 0x05) {
      ramBanks = 8;
    }
    else if(ramSize == 0x38) {  // 56
      ramBanks = 8;
    }
    else if(ramSize == 0xFF) { // 255
      ramBanks = 8;
    }
    else {
      ramBanks = 0;
    }
    Serial.println(ramBanks);

    // RAM end address
    if((ramSize == 0x00) && (cartridgeType == 0x06)) { // 
      ramEndAddress = 0x01FF;  // MBC2 512 bytes (01FF) (nibbles, 0,5kb) dec 41471 0xA1FF
    }
    else if(ramSize == 0x01) {
      ramEndAddress = 0xA7FF;  // 2K RAM, dec 43007
    }
    else if(ramSize == 0x02) {
      ramEndAddress = 0xBFFF;  // 8K RAM, dec 49151
    }
    else if(ramSize == 0x03) {
      ramEndAddress = 0x7FFF;  // 32K RAM, dec 49151
    }
    else if(ramSize == 0x04) {
      ramEndAddress = 0x01FFFF;  // 128K RAM, dec 49151
    }
    else if(ramSize == 0x05) {
      ramEndAddress = 0xFFFF;  // 64K RAM, dec 49151
    }
    else if(ramSize == 0x38) { // Beast Fighter (Taiwan) (Sachen)
      ramEndAddress = 0xFFFF;  
    }
    else if(ramSize == 0xFF) { // Action Replay Pro (Europe)
      ramEndAddress = 0xFFFF;  
    }
    else { // size = 0
      ramEndAddress = 0x0000; // ?? unknown check real ram adress, in io map maybe calc it
    }
    Serial.println(ramEndAddress, HEX);

    //----------
    // region of the game or multicard
    region = read_byte(0x014A);  // dec:330
    Serial.println(region);
    
    //-------------------
    // old & new licensee/developer/publisher of the game
    licensee = read_byte(0x014B); // dec: 331
    //Serial.println(licensee); 

    if(licensee == 0x0033) { // dec 51 "see new license code"
      for(uint16_t y = 0x0144; y <= 0x0145; y++) { // only 2 values
        licensee_new = read_byte(y); // dec: 331, int in py

      }
      Serial.println(licensee_new); // works as int

    }
    else {
      Serial.println(licensee); // works as int
    }

    //-------------
    /* 
      Mask ROM Version number
      Specifies the version number of the game. That is usually 00h */
    romver = read_byte(0x014C); // dec 332
    Serial.println(romver);
    //--------------
    /*
      https://gbdev.gg8.se/forums/viewtopic.php?id=317#:~:text=To%20calculate%20the%20header%20checksum,and%20ending%20with%20byte%2014C.&text=Now%2C%20this%20is%20why.,subtract%201%20from%20that%20result.
      http://www.enliten.force9.co.uk/gameboy/carthead.htm
    */
    headercs = read_byte(0x014D); // dec 333 complement checksum
    Serial.println(headercs);

    for(uint16_t c = 0x0134; c <= 0x014C; c++) { // if not enough then int16!
      hcheck = read_byte(c);
      z = z - hcheck - 1;
    }
    //Serial.println(z);

    /*
    for (uint16_t v = 0x00; v != 0x19; v++) { //dec 25
      h = h - p[v] - 1; // p is unknown
    }*/
    //Serial.println(h);

    if((headercs == z)) { // || (headercs == h)
      hcs = 1; // true check
    }
    else {
      hcs = 0; // false check
    }
    Serial.println(hcs); // works
    //---------------
    // 014E-014F - Global Checksum
    // Contains a 16 bit checksum (upper byte first) across the whole cartridge ROM. 
    // Produced by adding all bytes of the cartridge (except for the two checksum bytes). The Gameboy doesn't verify this checksum.
    uint16_t msb = read_byte(0x014E); // first
    uint16_t lsb = read_byte(0x014F); // last
    uint32_t stored_global_checksum = (msb << 8) | lsb;
    //Serial.println(stored_global_checksum);

    for(uint32_t k = 0x0000; k < romEndAddress; k++) { // rom_size_full
      if((k != 0x014E) && (k != 0x014F)) {
        uint8_t full_globalcs = read_byte(k);
        calculated_global_checksum += full_globalcs;
      }
    }
    //Serial.println(full_globalcs);
    //Serial.println(calculated_global_checksum);

    if(calculated_global_checksum == stored_global_checksum) {
      gcs = 1; // true check
    }
    else {
      gcs = 0; // false check
    }
    Serial.println(gcs);
    // after this the game should begin @ 0x0150 (336) normally with jump to game entry point, exeptions unknown
    //-------------------

  }
  // next menu option
  // Dump ROM
  else if(strstr(readInput, "READROM")) {
    rd_wr_mreq_reset();
    uint32_t romAddress = 0x00;

    // Read number of banks and switch banks
    for(uint8_t bank = 1; bank < romBanks; bank++) { // read all banks but maybe not correct
      if(cartridgeType >= 0x05) { // MBC2 and above
        write_byte(0x2100, bank); // Set ROM bank
      }
      else { // MBC1s
        write_byte(0x6000, 0); // Set ROM Mode
        write_byte(0x4000, bank >> 5); // Set bits 5 & 6 (01100000) of ROM bank
        write_byte(0x2000, bank & 0x1F); // Set bits 0 & 4 (00011111) of ROM bank
      }

      if(bank > 1) {
        romAddress = 0x4000; // dec 16.384
      }

      // Read up to 7FFF per bank
      while(romAddress <= 0x7FFF) { //dec 32.767

        for(uint8_t i = 0; i < 64; i++) { //0-63 =64
          readData[i] = read_byte(romAddress + i);
        }
        
        Serial.write(readData, 64); // Send the 64 byte chunk
        romAddress += 64;
      }

    }
      /*
        Serial.print("\nBANK_NUM: "); // debug
        Serial.print(bank);
      */
      //Serial.flush();
  }


  // next menu option
  // Read RAM
  else if(strstr(readInput, "READRAM")) {
    rd_wr_mreq_reset();

    // MBC2 Fix (unknown why this fixes reading the ram, maybe has to read ROM before RAM?)
    read_byte(0x0134);

    // if cartridge have RAM test
    if(ramEndAddress > 0x00) {
      if(cartridgeType <= 0x04) {  // MBC1
        write_byte(0x6000, 1);   // Set RAM Mode
      }

      // Initialise MBC
      write_byte(0x0000, 0x0A);

      // Switch RAM banks
      for(uint8_t bank = 0; bank < ramBanks; bank++) { // <= probieren statt nur <
        write_byte(0x4000, bank);

        // Read RAM
        for(uint16_t ramAddress = 0xA000; ramAddress <= ramEndAddress; ramAddress += 64) {
          uint8_t readData[64];
          for(uint8_t j = 0; j < 64; j++) {
            readData[j] = read_byte(ramAddress + j);
          }

          //Serial.println(readData,HEX);
          Serial.write(readData, 64);  // Send the 64 byte chunk

        }
      }

      // Disable RAM
      write_byte(0x0000, 0x00);
    }
  }

  // next menu option
  // Write RAM
  else if(strstr(readInput, "WRITERAM")) {
    rd_wr_mreq_reset();

    // MBC2 Fix (unknown why this fixes it, maybe has to read ROM before RAM?)
    read_byte(0x0134);

    // Does cartridge have RAM
    if(ramEndAddress > 0) {
      if(cartridgeType <= 0x04) {  // MBC1
        write_byte(0x6000, 1);   // Set RAM Mode
      }

      // Initialise MBC
      write_byte(0x0000, 0x0A); // 0A activates, 00 deactivates

      // Switch RAM banks
      for(uint8_t bank = 0; bank < ramBanks; bank++) { // maybe <= but complicated
        write_byte(0x4000, bank);

        // Write RAM
        for(uint16_t ramAddress = 0xA000; ramAddress <= ramEndAddress; ramAddress++) {
          // Wait for serial input
          while(Serial.available() <= 0) {
             // do nothig when waiting
          }

          // Read input
          uint8_t readValue = (uint8_t) Serial.read();

          // Write to RAM
          // maybe clock needed?
          aw_2.digitalWrite(GB_CS, LOW);
          aw_2.digitalWrite(GB_CLK, HIGH);
          write_byte(ramAddress, readValue);
          asm volatile("nop");
          asm volatile("nop");
          asm volatile("nop");
          aw_2.digitalWrite(GB_CS, HIGH);
          aw_2.digitalWrite(GB_CLK, LOW);
        }
      }

      // Disable RAM
      write_byte(0x0000, 0x00);

      // Flush any serial data that wasn't processed
      Serial.flush();
    }
    
  }
  
  // next menu option
  else if(strstr(readInput, "CLOCK")) { // debug clk pulse
    // test clock trigger
    //Serial.println("CLOCK TEST\n");
    aw_2.digitalWrite(GB_CLK, LOW);
    aw_2.digitalWrite(GB_CLK, HIGH);
    aw_2.digitalWrite(GB_CLK, LOW);
    //Serial.println("Done\n");
    Serial.flush();
  }

  // next menu option
  else if(strstr(readInput, "AUDIO")) {
    // terminate i2c + spi + serial
    //Serial.println("AUDIO TEST\n");
    gb_aud();
    Serial.flush();// Flush Waits for the transmission of outgoing serial data to complete
  }

  else if(strstr(readInput, "EXIT")) {
    // terminate i2c + spi + serial
    //Serial.println("EXITING!\nIf you want to use it again, you need to reset device!\n");
    // Flush Waits for the transmission of outgoing serial data to complete
    rd_wr_mreq_off(); // Set everying low
    aw_2.digitalWrite(GB_VIN, LOW);
    aw_2.digitalWrite(GB_VOLT, LOW);
    aw_1.reset();
    aw_2.reset();
    Serial.flush();
    Serial.end();
    //Wire.clearTimeout(); // newer func
    Wire.endTransmission();
    Wire.end();
    gb_reset();
  }

  // status reset
  //rd_wr_mreq_off();

}
//--- End loop! start function definitions
void wirereq () {
  //https://reference.arduino.cc/reference/en/language/functions/communication/wire/requestfrom/
  /*
  Wire.requestFrom(EX1, 1); // addr, quantity, stop
  char expander1 = Wire.read(); // returs next byte
  Serial.println(expander1);
  Serial.flush();
  */
  Wire.requestFrom(EX2, 1);
  char expander2 = Wire.read();
  Serial.println(expander2);
  Serial.flush();
}
  
void latchaddress(uint16_t addr) {
  aw_1.digitalWrite(addr, HIGH); // neccesary???
  aw_1.outputGPIO(addr); // sure with aw1 on analog pins?
  
}

// Use the shift registers to shift out the address
void shiftout_address(uint16_t shiftAddress) { // vermute, dass hier noch ein fehler vorliegt weil dump abbricht
  
  aw_2.digitalWrite(GB_CS, LOW); // not sure if correct
  //latchaddress(shiftAddress); // not sure probably strange
  // generally  latch => "now is the time to copy all the shifted data bits to the output register so they appear on the output pins"
/*
  AW9523_REG_INPUT0 (0x00):
  This register is used for reading input values from GPIO port 0.
  AW9523_REG_OUTPUT0 (0x02):
  This register is used for writing output values to GPIO port 0.
  AW9523_REG_CONFIG0 (0x04):
  This register is used for configuring the direction of GPIO port 0 (input or output).
*/
  
  //https://reference.arduino.cc/reference/de/language/functions/communication/wire/begintransmission/
  Wire.beginTransmission(EX2); // device addr
  //https://reference.arduino.cc/reference/de/language/functions/communication/wire/write/
  Wire.write(0x02); // send register address output
  Wire.write(shiftAddress >> 8); // Send MSB data!, shiftaddress maybe wrong
  Wire.write(shiftAddress & 0xFF); // Send LSB data
  Wire.endTransmission();
  
  asm volatile("nop");
  aw_2.digitalWrite(GB_CS, HIGH);

}

uint8_t read_byte(uint16_t address) {
  

  aw_2.digitalWrite(GB_CLK, HIGH);
  
  shiftout_address(address);  // Shift out address
  aw_2.digitalWrite(GB_CS, LOW);

  aw_2.digitalWrite(GB_RD, LOW);
 
  asm volatile("nop"); // Delay a little (minimum is 2 nops, using 3 to be sure)
  asm volatile("nop");
  asm volatile("nop");
  
  uint16_t save = aw_2.inputGPIO();
  //Serial.println(save, HEX);
  save &= 0x00FF; // dec 255, mask lower 8 byte 
  uint8_t bval = (uint8_t) save;  // Read data
  // uint8_t bval = ((PINB << 6) | (PIND >> 2)); // old code to compare, read data
  
  aw_2.digitalWrite(GB_RD, HIGH);
  aw_2.digitalWrite(GB_CS, HIGH);
  aw_2.digitalWrite(GB_CLK, LOW);

  return bval;
}

void write_byte(uint16_t address, uint8_t data) {

  aw_2.pinMode(GB_D0, OUTPUT);
  aw_2.pinMode(GB_D1, OUTPUT);
  aw_2.pinMode(GB_D2, OUTPUT);
  aw_2.pinMode(GB_D3, OUTPUT);
  aw_2.pinMode(GB_D4, OUTPUT);
  aw_2.pinMode(GB_D5, OUTPUT);
  aw_2.pinMode(GB_D6, OUTPUT);
  aw_2.pinMode(GB_D7, OUTPUT);
  
  shiftout_address(address);  // Shift out address

  uint16_t save = aw_2.inputGPIO();
  // clear outputs as original
  //uint16_t save &= ~(aw_2.inputGPIO());
  // lower 8 Bits of variable save are cleared and only upper 8 Bits are kept
  save &= 0xFF00; // not sure about address from brutzi
  save |= data; // brutzi added

  // old stuff from original
  //save |= (data << 2); // PORTD / equivalent to x = x & y bitwise AND operator
  //save |= (data >> 6); // PORTB
  
  aw_2.outputGPIO(save); // data
  Serial.write(save);  // Send the ? chunk

  //aw_2.digitalWrite(GB_CLK, HIGH);

  // Pulse WR
  aw_2.digitalWrite(GB_WR, LOW);
  asm volatile("nop");
  aw_2.digitalWrite(GB_WR, HIGH);

  //aw_2.digitalWrite(GB_CLK, LOW);
  
  // Set pins as inputs
  aw_2.pinMode(GB_D0, INPUT);
  aw_2.pinMode(GB_D1, INPUT);
  aw_2.pinMode(GB_D2, INPUT);
  aw_2.pinMode(GB_D3, INPUT);
  aw_2.pinMode(GB_D4, INPUT);
  aw_2.pinMode(GB_D5, INPUT);
  aw_2.pinMode(GB_D6, INPUT);
  aw_2.pinMode(GB_D7, INPUT);
  
}

// Turn /RD, /WR and MREQ to high so they are deselected (reset state)
void rd_wr_mreq_reset() { // mreq entspricht CS?
  aw_2.digitalWrite(GB_CLK, HIGH); // added idk if neccessary
  
  aw_2.digitalWrite(GB_RD, HIGH);  // /RD off
  aw_2.digitalWrite(GB_WR, HIGH);  // /WR off
  aw_2.digitalWrite(GB_CS, HIGH);  // /CS off, strange

  aw_2.digitalWrite(GB_CLK, LOW);
}

// Turn /RD, /WR and MREQ off as no power should be applied to GB Cart ?????
void rd_wr_mreq_off() {
  aw_2.digitalWrite(GB_CLK, HIGH);
  
  aw_2.digitalWrite(GB_RD, LOW);  // /RD on
  aw_2.digitalWrite(GB_WR, LOW);  // /WR on
  aw_2.digitalWrite(GB_CS, LOW);  // /CS off, strange

  aw_2.digitalWrite(GB_CLK, LOW);
}

// -------------- experimental!!! if ready it will be built-in to the upper code!!!
/*
uint16_t readDataBus() { // not used atm, (for gba before)
  uint16_t save = aw_2.inputGPIO();
  save &= 0x00FF; // 255 not sure if 00FF is correct?! second half masked
  uint16_t s = (uint8_t) save;  // Read data
  return s; // maybe use it to simplify other funcs
}
*/
// end  suggestion
void gb_aud() {
  //Serial.println("GB audio check\n");
  aw_2.digitalWrite(GB_CLK, HIGH);
  
  aw_2.digitalWrite(GB_VIN, HIGH); // on
  aw_2.digitalWrite(GB_VIN, LOW); // off
 
  aw_2.digitalWrite(GB_CLK, LOW);
  wirereq (); // just debug i2c
  // needs extra func in py
  //Serial.println("GB audio done \n");
  Serial.flush();
}

void gb_reset() {

  aw_2.digitalWrite(GB_CLK, HIGH);
  
  aw_2.digitalWrite(GB_RES, LOW); /// reset activate
  
  aw_2.digitalWrite(GB_CLK, LOW);

  asm volatile ("jmp 0"); // Jump to address 0 (soft reset)

}
// EOF
