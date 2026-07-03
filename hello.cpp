#include <iostream>

int main() {
    std::cout << "Hello from Ubuntu!" << std::endl;
	
    int age;
    std::string name;

    std::cout << "Enter age: ";
    std::cin >> age;  // User types "25" and presses ENTER

    std::cout << "Enter name: ";
    std::cin >> name; // Does it wait?     

    std::cout << "entered age:";
    std::cout << age << std::endl;

    std::cout << "entered name:";
	std::cout << name << std::endl;
return 0;
} // hello world 
