#include <algorithm>
#include <chrono>
#include <filesystem>
#include <iostream>
#include <sndfile.h>

double getFileDuration(const std::string& filePath){
    SF_INFO sfinfo;
    SNDFILE* file = sf_open(filePath.c_str(), SFM_READ, &sfinfo);
    if (file == nullptr) {
        std::cout << "Error reading file: " << filePath << std::endl;
        return 0.0;
    }
    double duration = static_cast<double>(sfinfo.frames) / sfinfo.samplerate;
    sf_close(file);
    return duration;
}

void printProgressBar(int processedFiles, int totalFiles, std::chrono::steady_clock::time_point startTime){
    using namespace std::chrono;
    float progress = static_cast<float>(processedFiles) / totalFiles;
    int barWidth = 100;
    auto now = steady_clock::now();
    auto elapsed = duration_cast<seconds>(now - startTime).count();

    int etaSeconds = static_cast<int>((elapsed / progress) - elapsed);
    int etaHours = etaSeconds / 3600;
    int etaMinutes = (etaSeconds % 3600) / 60;
    etaSeconds %= 60;

    std::cout << "[";
    int pos = static_cast<int>(barWidth * progress);
    for (int i = 0; i < barWidth; ++i){
        std::cout << (i < pos ? "=" : (i == pos ? ">" : " "));
    }
    std::cout << "] " << static_cast<int>(progress * 100.0) << "% " << processedFiles << "/" << totalFiles <<
        " ETA: " << std::setfill('0') << std::setw(2) << etaHours << ":" << std::setw(2) << etaMinutes << ":" << std::setw(2) << etaSeconds << "\r";
    std::cout.flush();
}

int main(int argc, char* argv[]){
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <folderPath>" << std::endl;
        return 1;
    }

    std::string folderPath = argv[1];
    auto startTime = std::chrono::steady_clock::now();

    std::cout << "Loading Files..." << std::endl;
    int fileCount = 0;
    for (const auto& entry : std::filesystem::recursive_directory_iterator(folderPath)) {
        if (!entry.is_regular_file()) continue;
        auto ext = entry.path().extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        if (ext == ".wav" || ext == ".ogg" || ext == ".opus" || ext == ".snd") {
            fileCount++;
        }
    }
    std::cout << "File Count: " << fileCount << std::endl;

    double totalDuration = 0.0;
    double maxDuration = 0.0;
    double minDuration = std::numeric_limits<double>::max();
    int processedFiles = 0;
    auto lastUpdate = std::chrono::steady_clock::now();
    std::chrono::milliseconds updateInterval(200);

    for (const auto& entry : std::filesystem::recursive_directory_iterator(folderPath)) {
        if (!entry.is_regular_file()) continue;

        auto ext = entry.path().extension().string();
        auto now = std::chrono::steady_clock::now();

        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        if (ext == ".wav" || ext == ".ogg" || ext == ".opus" || ext == ".snd") {
            double duration = getFileDuration(entry.path().string());
            totalDuration += duration;
            minDuration = std::min(minDuration, duration);
            maxDuration = std::max(maxDuration, duration);
            processedFiles++;
            auto now = std::chrono::steady_clock::now();

            if (now - lastUpdate > updateInterval) {
                printProgressBar(processedFiles, fileCount, startTime);
                lastUpdate = now;
            }
        }
    }
    std::cout << std::endl;

    if (minDuration == std::numeric_limits<double>::max()) {
        minDuration = 0.0; // In case no files were found
    }
    double totalDuration_hours = totalDuration / 3600;

    std::cout << "Total Duration: " << std::fixed << std::setprecision(2) << totalDuration_hours << " hours" << std::endl;
    std::cout << "Average: " << std::fixed << std::setprecision(2) << totalDuration / fileCount << " seconds" << std::endl;
    std::cout << "Shortest: " << std::fixed << std::setprecision(2) << minDuration << " seconds" << std::endl;
    std::cout << "Longest: " << std::fixed << std::setprecision(2) << maxDuration << " seconds" << std::endl;

    return 0;
}