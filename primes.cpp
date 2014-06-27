#include <iostream>
#include <vector>
#include <iterator> 
#include <stdlib.h> 

using namespace std;
int main(int argc, const char* argv[] ){
	if(argc < 2){
		cerr << "(Not enough arguments.. n is the upper bound)\n Usage: ./primes n" << endl;   
		exit (EXIT_FAILURE);   
	}
	int bound = atoi( argv[1] );
	vector<int> list(bound-1);
	int i = 0, j = 0;
	while(i < bound-1){
		list[i] = i + 2;
		i++;
	}
	int size = list.size();
	i = 0;
	int holder = list[i];
	while(true){
		while(j < size){
			int temp = list[j];
			if(temp%holder == 0 && temp/holder != 1 ){
				list.erase(list.begin()+j);
				j--;
			}
			j++;
			size = list.size();
		}
		size = list.size();
		i++;
		holder = list[i];
		j = i;
		if(holder >= bound) break;
	}
	i = 0;
        size = list.size();
        while (i < size){
                cout << list[i++] << "\t";
        }
	cout << endl;
	cout << "Number of primes less than or equal to " << bound << " is: " << size << endl;
	return 0;
}

