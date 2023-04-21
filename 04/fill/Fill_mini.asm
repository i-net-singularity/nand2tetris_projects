    @i
    M=0

(ON_LOOP)
    @SCREEN
    D=A
    
    @i
    A=D+M
    M=!M

    @i
    D=M

    @8190
    D=D-A

    @ON_END
    D;JGT

    @i
    MD=M+1

    @ON_LOOP
    0;JMP

(ON_END)
    @ON_END
    0;JMP

//(ON)
//    @SCREEN // スクリーンの開始アドレスを取得
//    D=A
//(FILL_BLACK)
//    @v_scr_pointer
//    D=M
//    //M=D     // スクリーンの現在アドレスを設定
//    A=D
//    M=!M    // 現在位置を反転（反転前は前提として白のため、黒に塗る）
//
//    @v_scr_pointer
//    D=M+1
//    M=D
//
//    @c_screen_max_address
//    D=D-M  // M&D = i - screen_max_address(8129)
//    @FILL_BLACK
//    D;JLT  // D < 0 ならば、(FILL_BLACK) にジャンプ
//    @LOOP
//    0;JMP
