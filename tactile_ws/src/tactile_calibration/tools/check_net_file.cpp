// OPTIONAL cross-check (NOT compiled/tested by the author): loads a NET_FILE.txt with the
// real legacy reader and evaluates it on CSV rows from stdin (25 comma-separated voltages
// per line), printing the wrench outputs. Compare with:
//   ros2 run tactile_calibration tactile_train predict --model NET_FILE.txt --inputs in.csv
#include <ANN/ANN_File_Reader.h>
#include <iostream>
#include <sstream>
#include <cstdio>

int main(int argc, char** argv)
{
  if (argc < 2) { std::cerr << "usage: check_net_file NET_FILE.txt < in.csv\n"; return 1; }
  ANN ann = readANNFile(argv[1]);
  std::string line;
  while (std::getline(std::cin, line))
  {
    for (char& c : line) if (c == ',') c = ' ';
    std::istringstream s(line);
    TooN::Vector<> v = TooN::Zeros(25);
    for (int i = 0; i < 25; i++) s >> v[i];
    TooN::Vector<> o = ann.compute(v);
    for (int i = 0; i < o.size(); i++) std::printf("%.10e%c", o[i], i + 1 < o.size() ? ',' : '\n');
  }
  return 0;
}
