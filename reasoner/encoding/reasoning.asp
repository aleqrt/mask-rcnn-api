%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%intersections along vertical axis or horizontal axis
inLevel(ID1, ID2, horizontal,"net") :-     net(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                net(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Ys1 <= Yd2, Yd1 >= Ys2.

inLevel(ID1, ID2, vertical,"net") :-     net(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                net(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Xs1 <= Xd2, Xd1 >= Xs2.
                                                
                                                
inLevel(ID1, ID2, horizontal,"cad") :-     cad(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                cad(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Ys1 <= Yd2, Yd1 >= Ys2.
                                                
                                                
inLevel(ID1, ID2, vertical,"cad") :-     cad(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                cad(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Xs1 <= Xd2, Xd1 >= Xs2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%calcolo la dimensione della box della Cad
distancePercentage(40).

box(W,L,"cad"):- #min{Xs1: cad(_,_,Xs1,_,_,_)} = K1, #max{Xs2: cad(_,_,_,_,Xs2,_)}= K2, W=K2-K1,
             #min{Ys1: cad(_,_,_,Ys1,_,_)} = K3, #max{Ys2: cad(_,_,_,_,_,Ys2)}= K4, L=K4-K3.

box(W,L,"net"):- #min{Xs1: net(_,_,Xs1,_,_,_)} = K1, #max{Xs2: net(_,_,_,_,Xs2,_)}= K2, W=K2-K1,
             #min{Ys1: net(_,_,_,Ys1,_,_)} = K3, #max{Ys2: net(_,_,_,_,_,Ys2)}= K4, L=K4-K3.

distanceThreshold(DW,DL,T):- distancePercentage(A), box(W,L,T), DW=W*A/100,DL=L*A/100.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


object(C1,ID1,X1,Y1,X2,Y2,"net"):- net(C1,ID1,X1,Y1,X2,Y2).
object(C1,ID1,X1,Y1,X2,Y2,"cad"):- cad(C1,ID1,X1,Y1,X2,Y2).

aux1(C1,ID1,T):-object(C1,ID1,X1,Y1,X2,Y2,T).
%aux1(C1,ID1,"net"):-object(C1,ID1,X1,Y1,X2,Y2,"net").

center(C,ID,C1,C2,T):- object(C,ID,X1,Y1,X2,Y2,T), C1=(X2+X1)/2, C2=(Y2+Y1)/2 .

squared_euc(ID1,ID2,D,T1,T2):- center(_,ID1,X1,Y1,T1),center(_,ID2,X2,Y2,T2), K1=X2-X1, K2=Y2-Y1, D=(K1*K1)+(K2*K2).

manhattan(ID1,ID2,D,T1,T2):- center(_,ID1,X1,Y1,T1),center(_,ID2,X2,Y2,T2), K1=X2-X1, K2=Y2-Y1, K1>=0, K2>=0, D=K1+K2.
manhattan(ID1,ID2,D,T1,T2):- center(_,ID1,X1,Y1,T1),center(_,ID2,X2,Y2,T2), K1=X2-X1, K2=Y2-Y1, K1<0, K2>=0, D=(K1*(-1))+K2.
manhattan(ID1,ID2,D,T1,T2):- center(_,ID1,X1,Y1,T1),center(_,ID2,X2,Y2,T2), K1=X2-X1, K2=Y2-Y1, K1>=0, K2<0, D=(K2*(-1))+K1.
manhattan(ID1,ID2,D,T1,T2):- center(_,ID1,X1,Y1,T1),center(_,ID2,X2,Y2,T2), K1=X2-X1, K2=Y2-Y1, K1<0, K2<0, D=(K2*(-1))+(K1*(-1)).


mapping(ID1,ID2)|noMapping(ID1,ID2):- aux1(C1,ID1,"cad"),aux1(C1,ID2,"net").

:- mapping(ID1,ID2), mapping(ID1,ID3),ID2!=ID3.
:- mapping(ID1,ID2), mapping(ID3,ID2),ID1!=ID3.

almeno1(ID1):-mapping(ID1,_).
:~ aux1(C1,ID1,"cad"), not almeno1(ID1). [1@2,ID1]


:~mapping(ID1,ID2), squared_euc(ID1,ID2,D,_,_). [D@1,ID1,ID2]

mappedCad(ID1):-mapping(ID1,_).
mappedNet(ID1):-mapping(_,ID1).

absent(C1,ID1):- aux1(C1,ID1,"cad"),  not mappedCad(ID1).
excess(C1,ID1):- aux1(C1,ID1,"net"),  not mappedNet(ID1).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

rel(ID1,ID2,"right",T):- manhattan(ID1,ID2,D,T,T), inLevel(ID1,ID2,horizontal,T),center(_,ID1,X1,_,T),center(_,ID2,X2,_,T), X1>X2, D = #min{K: manhattan(ID1,ID4,K,T,T),center(_,ID4,X4,_,T), X1>X4,inLevel(ID1,ID4,horizontal,T)}. 
rel(ID1,ID2,"top",T):- not inLevel(ID1,ID2,horizontal,T), manhattan(ID1,ID2,D,T,T), inLevel(ID1,ID2,vertical,T),center(_,ID1,_,Y1,T),center(_,ID2,_,Y2,T), Y1<Y2,D = #min{K: manhattan(ID1,ID4,K,T,T),not inLevel(ID1,ID4,horizontal,T),center(_,ID4,_,Y4,T), Y1<Y4,inLevel(ID1,ID4,vertical,T)}. 

limitedRel(ID1,ID2,D,"right",T):- rel(ID1,ID2,"right",T), manhattan(ID1,ID2,D,T,T), distanceThreshold(W,L,T), D<W.
limitedRel(ID1,ID2,D,"top",T):- rel(ID1,ID2,"top",T), manhattan(ID1,ID2,D,T,T), distanceThreshold(W,L,T), D<W.

%absentRel(C1,ID1,C2,ID2):-aux1(C1,ID1,"cad"), aux1(C2,ID2,"cad"),rel(ID1,ID2,"left","cad"),not rel(X,Y,"left","net"),mapping(ID1,X),mapping(ID2,Y).
%excessRel(C1,ID1,C2,ID2):-aux1(C1,ID1,"net"), aux1(C2,ID2,"net"),rel(ID1,ID2,"left","net"),not rel(X,Y,"left","cad"), mapping(X,ID1),mapping(Y,ID2).

blocks(ID1,ID2,C2,DIR,T):- auxLimited(ID1,ID2,DIR,T),aux1(C2,ID2,T).
blocks(ID1,ID3,C1,DIR,T):- blocks(ID1,ID2,C1,DIR,T),auxLimited(ID2,ID3,DIR,T),aux1(C1,ID3,T).

auxLimited(ID1,ID2,DIR,T):-limitedRel(ID1,ID2,D,DIR,T).

absentRel(C1,ID1,C2,ID2,X,Y):-  aux1(C1,ID1,"cad"), aux1(C2,ID2,"cad"), auxLimited(ID1,ID2,DIR,"cad"),
                                not blocks(X,Y,C2,DIR,"net"),not auxLimited(Y,X,DIR,"net"),
                                not auxLimited(X,Y,DIR,"net"),mapping(ID1,X),mapping(ID2,Y).
                                
excessRel(C1,ID1,C2,ID2):-      aux1(C1,ID1,"net"), aux1(C2,ID2,"net"),auxLimited(ID1,ID2,DIR,"net"),
                                not blocks(X,Y,C2,DIR,"cad"), not auxLimited(X,Y,DIR,"cad"), 
                                not auxLimited(Y,X,DIR,"cad"), mapping(X,ID1),mapping(Y,ID2).


                                
%absentRel(C1,ID1,C2,ID2):-  aux1(C1,ID1,"cad"), aux1(C2,ID2,"cad"), auxLimited(ID1,ID2,DIR,"cad"),
%                                mapping(ID1,X),absent(C2,ID2).

%absentRel(C1,ID1,C2,ID2):-  aux1(C1,ID1,"cad"), aux1(C2,ID2,"cad"), auxLimited(ID1,ID2,DIR,"cad"),
%                                absent(C1,ID1),mapping(ID2,X).
                              
%absentRel(C1,ID1,C2,ID2):-  aux1(C1,ID1,"cad"), aux1(C2,ID2,"cad"), auxLimited(ID1,ID2,DIR,"cad"),
%                                absent(C2,Y),absent(C1,ID1).
                                
%excessRel(C1,ID1,C2,Y):-  aux1(C1,ID1,"net"), aux1(C2,ID2,"net"),auxLimited(ID1,ID2,DIR,"net"),
%                            excess(C1,ID1),mapping(Y,ID2).
                            
%excessRel(C1,X,C2,ID2):-  aux1(C1,ID1,"net"), aux1(C2,ID2,"net"),auxLimited(ID1,ID2,DIR,"net"),
%                            excess(C2,ID2),mapping(X,ID1).

%excessRel(C1,ID1,C2,ID2):-  aux1(C1,ID1,"net"), aux1(C2,ID2,"net"),auxLimited(ID1,ID2,DIR,"net"),
%                            excess(C2,ID2),excess(C1,ID1).
