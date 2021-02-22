%schema componente(Label, Id, Xs, Ys, Xd, Yd)
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

compNonPresente(X) :- cad(X, _, _, _, _, _), not netAux(X).
netAux(X) :- net(X, _, _, _, _, _).

compInEccesso(X) :- net(X, _, _, _, _, _), not cadAux(X).
cadAux(X) :- cad(X, _, _, _, _, _).

errorePos(X, Id) :- posRelCad(X, _, Y, _, _), 
                    posRelNet(Y, Id, X, _, _), X!=Y.
                      
errorePos(Y, Id) :- posRelCad(X, _, Y, _, _), 
                    posRelNet(Y, _, X, Id, _), X!=Y.

noRelCad(X, Id1, Y, Id2) :- not #count{X,Y : posRelCad(X, _, Y, _, _)} >= 1, posRelNet(X, Id1, Y, Id2, _).
noRelNet(X, Id1, Y, Id2) :- not #count{X,Y : posRelNet(X, _, Y, _, _)} >= 1, posRelCad(X, Id1, Y, Id2, _).
