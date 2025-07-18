#include <iostream>
#include <cstdlib>

int main()
{
    std::cout << "C++ Worker: Starting execution..." << std::endl;
    const char *command = "python3 ./script.py";
    int returnValue = system(command);

    if (returnValue == 0)
    {
        std::cout << "Script successfully exec" << std::endl;
    }
    else
    {
        std::cout << "Script failed exec: " << returnValue << std::endl;
    }
    std::cout << "C++ Worker: Finished execution." << std::endl;
    return 0;
}