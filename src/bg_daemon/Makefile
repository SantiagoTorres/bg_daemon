EX=quack
CC=cc
FRAMEWORKS = -framework Foundation -framework AppKit
CFLAGS += -fobjc-arc $(FRAMEWORKS)
#  Main target
all: $(EX)

quack:
	$(CC) $(CFLAGS) -o $(EX) main.m

#  Delete unwanted files
clean:
	rm -f $(EX) *.o

