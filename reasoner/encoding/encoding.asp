%schema componente(Label, Id, Bottom_Left_Xs, Bottom_Left_Ys, Top_Right_Xd, Top_Right_Yd)
%schema posizioneRelativa(Label_1, ID_1, Label_2, ID_2, Position)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

posRelAllCad(C1, ID1, C2, ID2, left) :- cad(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                        cad(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                        ID1 <> ID2,
                                        Xd2 > Xd1,
                                        inLevelCad(C1, ID1, C2, ID2, horizontal).
                                    
somethingInTheMiddleCad(C1, ID1, C3, ID3, left) :-  posRelAllCad(C1, ID1, C2, ID2, left),
        								            cad(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                    cad(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                    cad(C3, ID3, Xs3, Ys3, Xd3, Yd3),
                                                    ID1 <> ID2, ID3 <> ID2, ID3 <> ID1,
                                                    Xd2 > Xd1,
                                                    Xd3 > Xd2,
                                                    inLevelCad(C1, ID1, C3, ID3, horizontal),
                                                    inLevelCad(C1, ID1, C2, ID2, horizontal).

posRelCad(C1, ID1, C2, ID2, left):- posRelAllCad(C1, ID1, C2, ID2, left), not somethingInTheMiddleCad(C1, ID1, C2, ID2, left).


%Components in Levels
inLevelCad(C1, ID1, C2, ID2, horizontal) :-     cad(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                cad(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Ys1 <= Yd2, Yd1 >= Ys2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

posRelAllNet(C1, ID1, C2, ID2, left) :-     net(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                            net(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                            ID1 <> ID2,
                                            Xd2 > Xd1,
                                            inLevelNet(C1, ID1, C2, ID2, horizontal).
                                    
somethingInTheMiddleNet(C1, ID1, C3, ID3, left) :-      posRelAllNet(C1, ID1, C2, ID2, left),
            								            net(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                        net(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                        net(C3, ID3, Xs3, Ys3, Xd3, Yd3),
                                                        ID1 <> ID2, ID3 <> ID2, ID3 <> ID1,
                                                        Xd2 > Xd1,
                                                        Xd3 > Xd2,
                                                        inLevelNet(C1, ID1, C3, ID3, horizontal),
                                                        inLevelNet(C1, ID1, C2, ID2, horizontal).

posRelNet(C1, ID1, C2, ID2, left):- posRelAllNet(C1, ID1, C2, ID2, left), not somethingInTheMiddleNet(C1, ID1, C2, ID2, left).


%Components in Levels
inLevelNet(C1, ID1, C2, ID2, horizontal) :-     net(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                net(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Ys1 <= Yd2, Yd1 >= Ys2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Componenti che sono presenti nel CAD ma non nella RETE
compNonPresente(X) :- cad(X, _, _, _, _, _), not netAux(X).
netAux(X) :- net(X, _, _, _, _, _).

%Componenti che sono presenti nella RETE ma non nel CAD
compInEccesso(X) :- net(X, _, _, _, _, _), not cadAux(X).
cadAux(X) :- cad(X, _, _, _, _, _).

%Identifica le relazioni che sono presenti tra due componenti nella RETE ma non nel CAD
noRelCad(X, Id1, Y, Id2) :- not #count{X,Y : posRelCad(X, _, Y, _, _)} >= 1, posRelNet(X, Id1, Y, Id2, _).

%Identifica le relazioni che sono presenti tra due componenti nel CAD ma non nella RETE
noRelNet(X, Id1, Y, Id2) :- not #count{X,Y : posRelNet(X, _, Y, _, _)} >= 1, posRelCad(X, Id1, Y, Id2, _).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Di seguito N e C fanno riferimento agli ID !!!!!!!

% Identificazione del componente successivo
succCad(C1, C2):- posRelCad(_, C1, _, C2, _).
succNet(N1, N2):- posRelNet(_, N1, _, N2, _).

% GUESS di tutti i possibili match tra i grafi
match(N,C) | nMatch(N,C) :- net(_, N, _, _, _, _),cad(_, C, _, _, _, _).

:- #count{ N : match(N,C) }= 1, cad(_, C, _, _, _, _).
:- #count{ C : match(N,C) }= 1, net(_, N, _, _, _, _).


% Non è possibile che ci sia un match tra due componenti che non abbiano la stessa label
:- net(L1, N, _, _, _, _), cad(L2,C,  _, _, _, _), match(N,C), L1!=L2.

% Non è possibile che due componenti individuati come successivi e che fanno un match nella RETE non lo siano nel CAD
% e viceversa
:- succNet(N1,N2),  not succCad(C1,C2), match(N1,C1), match(N2,C2).
:- not succNet(N1,N2), succCad(C1,C2), match(N1,C1), match(N2,C2).

erroreNet(N1):- net(N1), not matchAux(N1).
matchAux(N1):- match(N1,_).

erroreCad(C1):- cad(C1), not matchAuxCad(C1).
matchAuxCad(C1):- match(_,C1).

:~ nMatch(X,Y). [1@1,X,Y]
