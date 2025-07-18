#include <iostream>
#include <string>
#include <fstream>
#include <cstdlib>

int main()
{
    std::cout << "C++ Worker: Starting execution..." << std::endl;
    
    std::string script_content;
    std::string line;

    while (std::getline(std::cin, line)) {
        script_content += line + "\n";
    }

    if (script_content.empty()) {
        std::cerr << "C++ Worker: No script content received from stdin. Exiting." << std::endl;
        return 1;
    }

    std::ofstream temp_script_file("temp_script.py");
    temp_script_file << script_content;
    temp_script_file.close();

    // The command to execute our temporary script
    const char* command = "python3 ./temp_script.py";
    int returnValue = system(command);

    if (returnValue == 0) {
        std::cout << "C++ Worker: Script executed successfully." << std::endl;
    } else {
        std::cerr << "C++ Worker: Script execution failed." << std::endl;
    }
    
    return returnValue;
    
}