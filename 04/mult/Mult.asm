// This file is part of www.nand2tetris.orgゲート
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

    @i     // カウンタ変数
    M=1    // i = 1 
    @R2    // 結果を格納する仮想レジスタ
    M=0    // R2 = 0
(LOOP)
    @i
    D=M    // レジスタ「D」に　メモリ[i] を セット
    @R1    // 乗数を格納する仮想レジスタ（値はプログラム実行前に手動セットアップする）
    D=D-M  // D = i - R1
    @END
    D;JGT  // D > 0 ならば、(END) にジャンプ
    @R0    // 被乗数を格納する仮想レジスタ（値はプログラム実行前に手動セットアップする）
    D=M    // D = R0
    @R2
    M=D+M  // R2 += R0
    @i
    M=M+1  // i++
    @LOOP
    0;JMP  // (LOOP) に無条件ジャンプ
(END)
    @END   // 無限ループ
    0;JMP
