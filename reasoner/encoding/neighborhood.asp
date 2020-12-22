%schema component(Label, Id, X1, Y1, X2, Y2, X3, Y3, X4, Y4)
%schema neighbour(Label_1, ID_1, Label_2, ID_2, Position)

%Si suppone siano componenti quadrati non piegati

neighbourAll(C1, ID1, C2, ID2, left) :- component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
											component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4), C1 <> C2, 
											inLevel(C1, ID1, C2, ID2, horizontal),
											IX2 <= IIX1.
somethingInTheMiddle(C1, ID1, C2, ID2, left) :- neighbourAll(C1, ID1, C2, ID2, left),
														component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
														component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4),
													component(C3, ID3, IIIX1, IIIY1, IIIX2, IIIY2, IIIX3, IIIY3, IIIX4, IIIY4),
													C3 <> C1, C3 <> C2,
													inLevel(C1, ID1, C3, ID3, horizontal),
													IX2 <= IIIX1, IIIX2 <= IIX1.

neighbourAll(C1, ID1, C2, ID2, bottom) :- component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
											component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4), C1 <> C2, 
											inLevel(C1, ID1, C2, ID2, vertical),
											IY1 <= IIY3.
somethingInTheMiddle(C1, ID1, C2, ID2, bottom) :- neighbourAll(C1, ID1, C2, ID2, bottom),
														component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
														component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4),
													component(C3, ID3, IIIX1, IIIY1, IIIX2, IIIY2, IIIX3, IIIY3, IIIX4, IIIY4),
													C3 <> C1, C3 <> C2,
													inLevel(C1, ID1, C3, ID3, vertical),
													IY1 <= IIIY3, IIIY1 <= IIY3.

 
neighbour(C1, ID1, C2, ID2, Dir) :- neighbourAll(C1, ID1, C2, ID2, Dir), not somethingInTheMiddle(C1, ID1, C2, ID2, Dir).
neighbour(C2, ID2, C1, ID1, right) :- neighbour(C1, ID1, C2, ID2, left).
neighbour(C2, ID2, C1, ID1, top) :- neighbour(C1, ID1, C2, ID2, bottom).


%Components in Levels

%THE COMMENTED RULES REFER TO COMPONENTS WHICH CLOSELY CLOSE
%inLevel(C1, ID1, C2, ID2, horizontal) :- component(C1, ID1, X1, Y1, X2, Y2, X3, Y3, X4, Y4), 
%									component(C2, ID2, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), C1 <> C2,
%										IY1 <= Y1, IY3 >= Y3.
%
%inLevel(C1, ID1, C2, ID2, horizontal) :- component(C1, ID1, X1, Y1, X2, Y2, X3, Y3, X4, Y4), 
%									component(C2, ID2, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), C1 <> C2,
%										IY1 <= Y1, IY3 <= Y3, D = Y3 - IY3, D < 5000.

inLevel(C1, ID1, C2, ID2, horizontal) :- component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
									component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4), C1 <> C2,
										IIY1 >= IY3, IIY1 <= IY2.
inLevel(C1, ID1, C2, ID2, horizontal) :- component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
									component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4), C1 <> C2,
										IIY3 >= IY3, IIY3 <= IY2.


inLevel(C1, ID1, C2, ID2, vertical) :- component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
									component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4), C1 <> C2,
										IIX1 >= IX1, IIX1 <= IX2.

inLevel(C1, ID1, C2, ID2, vertical) :- component(C1, ID1, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), 
									component(C2, ID2, IIX1, IIY1, IIX2, IIY2, IIX3, IIY3, IIX4, IIY4), C1 <> C2,
										IIX2 >= IX1, IIX2 <= IX2.


inLevel(C1, ID1, C2, ID2, V) :- inLevel(C2, ID2, C1, ID1, V).



% My RAGIONAMENTO DI TEST
%noNeighbour(ID1, ID2) :- component(C1, ID1, _, _, _, _, _, _, _, _), component(C2, ID2, _, _, _, _, _, _, _, _), not neighbour(C1, ID1, C2, ID2, horizontal).




%neighbour2(C1, ID1, C2, ID2, horizontal) :- 	component(C1, ID1, X1, Y1, X2, Y2, X3, Y3, X4, Y4), 
%								component(C2, ID2, IX1, IY1, IX2, IY2, IX3, IY3, IX4, IY4), C1 <> C2, 
%								inLevel(C1, ID1, C2, ID2, horizontal),
%									X2 <= IX1, D = IX1 - X2, D < 1000. 

%more(ID1, ID2) :- neighbour2(C1, ID1, C2, ID2, horizontal), not neighbour(C1, ID1, C2, ID2, horizontal).

