#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <pqxx/pqxx>
#include <sstream> // Required for this new method

// Function to capture output from a system command
std::string exec(const char* cmd) {
    char buffer[128];
    std::string result = "";
    FILE* pipe = popen(cmd, "r");
    if (!pipe) throw std::runtime_error("popen() failed!");
    try {
        while (fgets(buffer, sizeof buffer, pipe) != NULL) {
            result += buffer;
        }
    } catch (...) {
        pclose(pipe);
        throw;
    }
    pclose(pipe);
    return result;
}

int main() {
    // --- NEW, MORE ROBUST WAY TO READ FROM STDIN ---
    std::stringstream buffer;
    buffer << std::cin.rdbuf();
    std::string job_info = buffer.str();
    // --- END OF NEW METHOD ---

    std::string delimiter = "|||";
    size_t pos = job_info.find(delimiter);
    if (pos == std::string::npos) {
        std::cerr << "Worker Error: Invalid message format received." << std::endl;
        return 1;
    }
    std::string job_id = job_info.substr(0, pos);
    std::string script_code = job_info.substr(pos + delimiter.length());
    
    std::cout << "Worker Info: Processing job ID " << job_id << std::endl;

    try {
        pqxx::connection C("dbname=analytics user=user password=password host=db port=5432");
        pqxx::work W1(C);
        W1.exec("UPDATE jobs SET status = 'RUNNING' WHERE job_id = '" + W1.esc(job_id) + "'");
        W1.commit();
        
        std::ofstream temp_script_file("temp_script.py");
        temp_script_file << script_code;
        temp_script_file.close();

        std::string full_output = exec("python3 ./temp_script.py");

        std::string text_result = full_output;
        std::string image_result = "";
        
        std::string start_delim = "---PLOT_START---";
        std::string end_delim = "---PLOT_END---";
        
        size_t start_pos = full_output.find(start_delim);
        size_t end_pos = full_output.find(end_delim);

        if (start_pos != std::string::npos && end_pos != std::string::npos) {
            start_pos += start_delim.length();
            image_result = full_output.substr(start_pos, end_pos - start_pos);
            text_result = full_output.substr(0, full_output.find(start_delim));
        }

        pqxx::work W2(C);
        W2.exec("UPDATE jobs SET status = 'COMPLETED', result_text = '" + W2.esc(text_result) + "', result_image = '" + W2.esc(image_result) + "' WHERE job_id = '" + W2.esc(job_id) + "'");
        W2.commit();
        std::cout << "Worker Info: Job " << job_id << " completed successfully." << std::endl;
        C.disconnect();

    } catch (const std::exception &e) {
        std::cerr << "Worker Error: " << e.what() << std::endl;
        // In a real app, you would also update the job status to FAILED here
        return 1;
    }
    return 0;
}