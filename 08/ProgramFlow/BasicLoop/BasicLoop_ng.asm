@256 // 0
D=A // 1
@SP // 2
M=D // 3
@Sys.initRET0 // 4
D=A // 5
@SP // 6
A=M // 7
M=D // 8
@SP // 9
M=M+1 // 10
@LCL // 11
D=M // 12
@SP // 13
A=M // 14
M=D // 15
@SP // 16
M=M+1 // 17
@ARG // 18
D=M // 19
@SP // 20
A=M // 21
M=D // 22
@SP // 23
M=M+1 // 24
@THIS // 25
D=M // 26
@SP // 27
A=M // 28
M=D // 29
@SP // 30
M=M+1 // 31
@THAT // 32
D=M // 33
@SP // 34
A=M // 35
M=D // 36
@SP // 37
M=M+1 // 38
@SP // 39
D=M // 40
@LCL // 41
M=D // 42
@5 // 43
D=D-A // 44
@ARG // 45
M=D // 46
@Sys.init // 47
0;JMP // 48
(Sys.initRET0)
//////
// BasicLoop
// push constant 0
@0 // 49
D=A // 50
@SP // 51
A=M // 52
M=D // 53
@SP // 54
M=M+1 // 55
// pop local 0
@LCL // 56
D=M // 57
@0 // 58
A=D+A // 59
D=A // 60
@R13 // 61
M=D // 62
@SP // 63
M=M-1 // 64
A=M // 65
D=M // 66
@R13 // 67
A=M // 68
M=D // 69
// label LOOP_START
(BasicLoop$LOOP_START)
// push argument 0
@ARG // 70
D=M // 71
@0 // 72
A=D+A // 73
D=M // 74
@SP // 75
A=M // 76
M=D // 77
@SP // 78
M=M+1 // 79
// push local 0
@LCL // 80
D=M // 81
@0 // 82
A=D+A // 83
D=M // 84
@SP // 85
A=M // 86
M=D // 87
@SP // 88
M=M+1 // 89
// add
@SP // 90
M=M-1 // 91
A=M // 92
D=M // 93
@SP // 94
M=M-1 // 95
@SP // 96
A=M // 97
M=M+D // 98
@SP // 99
M=M+1 // 100
// pop local 0
@LCL // 101
D=M // 102
@0 // 103
A=D+A // 104
D=A // 105
@R13 // 106
M=D // 107
@SP // 108
M=M-1 // 109
A=M // 110
D=M // 111
@R13 // 112
A=M // 113
M=D // 114
// push argument 0
@ARG // 115
D=M // 116
@0 // 117
A=D+A // 118
D=M // 119
@SP // 120
A=M // 121
M=D // 122
@SP // 123
M=M+1 // 124
// push constant 1
@1 // 125
D=A // 126
@SP // 127
A=M // 128
M=D // 129
@SP // 130
M=M+1 // 131
// sub
@SP // 132
M=M-1 // 133
A=M // 134
D=M // 135
@SP // 136
M=M-1 // 137
@SP // 138
A=M // 139
M=M-D // 140
@SP // 141
M=M+1 // 142
// pop argument 0
@ARG // 143
D=M // 144
@0 // 145
A=D+A // 146
D=A // 147
@R13 // 148
M=D // 149
@SP // 150
M=M-1 // 151
A=M // 152
D=M // 153
@R13 // 154
A=M // 155
M=D // 156
// push argument 0
@ARG // 157
D=M // 158
@0 // 159
A=D+A // 160
D=M // 161
@SP // 162
A=M // 163
M=D // 164
@SP // 165
M=M+1 // 166
// if-goto LOOP_START
@SP // 167
M=M-1 // 168
A=M // 169
D=M // 170
@BasicLoop$LOOP_START // 171
D;JNE // 172
// push local 0
@LCL // 173
D=M // 174
@0 // 175
A=D+A // 176
D=M // 177
@SP // 178
A=M // 179
M=D // 180
@SP // 181
M=M+1 // 182