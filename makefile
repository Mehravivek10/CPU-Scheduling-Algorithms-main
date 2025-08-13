CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -Wpedantic
TARGET := lab4
SRC := main.cpp
OBJ := $(SRC:.cpp=.o)

.PHONY: all clean run ui

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp parser.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

run: $(TARGET)
	./$(TARGET)

ui:
	cd ui && . .venv/bin/activate 2>/dev/null || python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && uvicorn server:app --host 0.0.0.0 --port 8000

clean:
	rm -f $(OBJ) $(TARGET)
	
