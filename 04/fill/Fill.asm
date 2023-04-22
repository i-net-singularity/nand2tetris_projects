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

(LOOP)
    @i                    // カウンタ変数
    M=0                   // i = 0 

    @KBD                  // キーボードのアドレス
    D=M                   // キーボード入力を「D」に格納

    @BLACK_FILL
    D;JNE                 // D != 0 ならば、(LOOP_BLACK_FILL) にジャンプ

    @WHITE_FILL
    0;JMP                 // 上記以外ならば、(LOOP_WHITE_FILL) にジャンプ

(BLACK_FILL)

    @i
    D=M                   // D = i を取得

    @8192                 // スクリーンマップ(512 x 256) サイズ
    D=D-A                 // D = i - 8192

    @LOOP
    D;JGE                 // D >= 0 ならば、画面塗りつぶし完了なので (LOOP) にジャンプ

    @SCREEN
    D=A                   // スクリーンの開始アドレスを取得

    @i
    A=D+M                 // 操作対象のスクリーンアドレス = @SCREEN + i
    M=-1                  // 操作対象のスクリーンアドレスを黒で塗りつぶす（0xffff を設定）

    @i
    M=M+1                 // i++

    @BLACK_FILL
    0;JMP                 // (BLACK_FILL) に無条件ジャンプ

(WHITE_FILL)

    @i
    D=M                   // D = i を取得

    @8192                 // スクリーンマップ(512 x 256) サイズ
    D=D-A                 // D = i - 8192

    @LOOP
    D;JGE                 // D >= 0 ならば、画面塗りつぶし完了なので (LOOP) にジャンプ

    @SCREEN
    D=A                   // スクリーンの開始アドレスを取得

    @i
    A=D+M                 // 操作対象のスクリーンアドレス = @SCREEN + i
    M=0                   // 操作対象のスクリーンアドレスを白で塗りつぶす（0x0000 を設定）

    @i
    M=M+1                 // i++

    @WHITE_FILL
    0;JMP                 // (WHITE_FILL) に無条件ジャンプ

