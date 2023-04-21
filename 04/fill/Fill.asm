// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// 初期化


// ループ
(LOOP)
    @i                    // カウンタ変数
    M=0                   // i = 0 

    @KBD    // キーボードのアドレス
    D=M     // キーボード入力を「D」に格納
    @ON_LOOP
    D;JNE   // D != 0 ならば、(ON) にジャンプ
    @OFF_LOOP
    0;JMP   // 上記以外ならば、(OFF) にジャンプ

(ON_LOOP)
    @SCREEN
    D=A
    
    @i
    A=D+M
    D=0
    M=!D

    @i
    D=M

    @8190
    D=D-A

    @LOOP
    D;JGT

    @i
    MD=M+1

    @ON_LOOP
    0;JMP

(OFF_LOOP)
    @SCREEN
    D=A
    
    @i
    A=D+M
    D=0
    M=D

    @i
    D=M

    @8190
    D=D-A

    @LOOP
    D;JGT

    @i
    MD=M+1

    @OFF_LOOP
    0;JMP

