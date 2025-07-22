#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <pqxx/pqxx> // PostgreSQL C++ library header

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
    // --- Read job info from stdin ---
    std::string job_info;
    std::string line;
    while (std::getline(std::cin, line)) {
        job_info += line + "\n";
    }

    // --- Parse job_id and script_code ---
    std::string delimiter = "|||";
    size_t pos = job_info.find(delimiter);
    if (pos == std::string::npos) {
        std::cerr << "Worker Error: Invalid message format received." << std::endl;
        return 1;
    }
    std::string job_id = job_info.substr(0, pos);
    std::string script_code = job_info.substr(pos + delimiter.length());

    std::cout << "Worker Info: Processing job ID " << job_id << std::endl;

    // --- Connect to PostgreSQL ---
    pqxx::connection C("dbname=analytics user=user password=password host=db port=5432");
    if (!C.is_open()) {
        std::cerr << "Worker Error: Can't open database" << std::endl;
        return 1;
    }

    try {
        // --- Update status to RUNNING ---
        pqxx::work W1(C);
        W1.exec("UPDATE jobs SET status = 'RUNNING' WHERE job_id = '" + W1.esc(job_id) + "'");
        W1.commit();

        // --- Write script to file and execute ---
        std::ofstream temp_script_file("temp_script.py");
        temp_script_file << script_code;
        temp_script_file.close();

        std::string result = exec("python3 ./temp_script.py");

        // --- Update status to COMPLETED with result ---
        pqxx::work W2(C);
        W2.exec("UPDATE jobs SET status = 'COMPLETED', result = '" + W2.esc(result) + "' WHERE job_id = '" + W2.esc(job_id) + "'");
        W2.commit();
        std::cout << "Worker Info: Job " << job_id << " completed successfully." << std::endl;

    } catch (const std::exception &e) {
        // --- Update status to FAILED on error ---
        try {
            pqxx::work W3(C);
            W3.exec("UPDATE jobs SET status = 'FAILED', result = '" + W3.esc(e.what()) + "' WHERE job_id = '" + W3.esc(job_id) + "'");
            W3.commit();
        } catch (const std::exception &e2) {
            std::cerr << "Worker Error: Failed to update DB on error. " << e2.what() << std::endl;
        }
        std::cerr << "Worker Error: " << e.what() << std::endl;
        C.disconnect();
        return 1;
    }
    C.disconnect();
    return 0;
}