#include <algorithm>
#include <chrono>
#include <filesystem>
#include <iostream>
#include <thread>
#include <mutex>
#include <samplerate.h>
#include <sndfile.h>

std::mutex printMutex;

bool resampleAudioFile(const std::string& inputFilePath, const std::string& inputRootPath, const std::string& outputRootPath){
    std::filesystem::path inputPath(inputFilePath);
    std::filesystem::path rootInputPath(inputRootPath);
    std::filesystem::path relativePath = std::filesystem::relative(inputPath, rootInputPath);

    relativePath.replace_extension(".wav");

    std::filesystem::path outputPath = std::filesystem::path(outputRootPath) / relativePath;
    std::filesystem::create_directories(outputPath.parent_path());

    SF_INFO readFileInfo, writeFileInfo;
    SNDFILE* readFile = sf_open(inputFilePath.c_str(), SFM_READ, &readFileInfo);
    if (readFile == nullptr) {
        std::cerr << "Error reading file: " << inputFilePath << std::endl;
        return false;
    }

    // Set up the conversion parameters for libsamplerate
    int error;
    SRC_STATE* src_state = src_new(SRC_SINC_MEDIUM_QUALITY, readFileInfo.channels, &error);
    if (src_state == nullptr) {
        std::cerr << "Error creating SRC_STATE: " << src_strerror(error) << std::endl;
        sf_close(readFile);
        return false;
    }

    // Prepare the write file info
    writeFileInfo = readFileInfo;
    writeFileInfo.samplerate = 44100; // Target sample rate
    writeFileInfo.format = (SF_FORMAT_WAV | SF_FORMAT_PCM_16); // Target format

    SNDFILE* writeFile = sf_open(outputPath.string().c_str(), SFM_WRITE, &writeFileInfo);
    if (writeFile == nullptr) {
        std::cerr << "Error writing file: " << outputPath << std::endl;
        src_delete(src_state);
        sf_close(readFile);
        return false;
    }

    const int bufferSize = 4096;
    float inputBuffer[bufferSize];
    float outputBuffer[bufferSize];
    SRC_DATA src_data;
    src_data.data_in = inputBuffer;
    src_data.data_out = outputBuffer;
    src_data.src_ratio = static_cast<double>(writeFileInfo.samplerate) / readFileInfo.samplerate;
    src_data.end_of_input = 0; // False

    while (true) {
        src_data.input_frames = sf_readf_float(readFile, inputBuffer, bufferSize / readFileInfo.channels) / readFileInfo.channels;
        if (src_data.input_frames < bufferSize / readFileInfo.channels) src_data.end_of_input = SF_TRUE; // True if this is the last chunk

        src_data.output_frames = bufferSize / writeFileInfo.channels;
        error = src_process(src_state, &src_data);
        if (error) {
            std::cerr << "Error processing resample: " << src_strerror(error) << std::endl;
            break;
        }

        if (src_data.output_frames_gen > 0) {
            sf_writef_float(writeFile, outputBuffer, src_data.output_frames_gen);
        }

        if (src_data.end_of_input) break; // Exit the loop if we've processed all the input
    }

    src_delete(src_state);
    sf_close(readFile);
    sf_close(writeFile);

    return true;
}

void printProgressBar(int processedFiles, int totalFiles, std::chrono::steady_clock::time_point startTime) {
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
    for (int i = 0; i < barWidth; ++i) {
        std::cout << (i < pos ? "=" : (i == pos ? ">" : " "));
    }
    std::cout << "] " << static_cast<int>(progress * 100.0) << "% " << processedFiles << "/" << totalFiles <<
        " ETA: " << std::setfill('0') << std::setw(2) << etaHours << ":" << std::setw(2) << etaMinutes << ":" << std::setw(2) << etaSeconds << "\r";
    std::cout.flush();
}

void processFilesBatch(const std::vector<std::filesystem::path>& files, const std::filesystem::path& inputRootPath, const std::filesystem::path& outputRootPath, int& processedFilesCounter, int totalFiles, const std::chrono::steady_clock::time_point& startTime){
    auto lastUpdate = std::chrono::steady_clock::now();
    std::chrono::milliseconds updateInterval(1000);

    for (const auto& filePath : files) {
        if (resampleAudioFile(filePath.string(), inputRootPath.string(), outputRootPath.string())) {
            std::lock_guard<std::mutex> counterLock(printMutex); // 保护共享资源：processedFilesCounter
            processedFilesCounter++;
            auto now = std::chrono::steady_clock::now();

            if (now - lastUpdate > updateInterval) {
                printProgressBar(processedFilesCounter, totalFiles, startTime);
                lastUpdate = now;
            }
        }
        else {
            std::cerr << "Failed to process file: " << filePath << std::endl;
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <inputFolderPath> <outputFolderPath>\n";
        return 1;
    }

    std::filesystem::path inputFolderPath = argv[1];
    std::filesystem::path outputFolderPath = argv[2];
    std::filesystem::create_directories(outputFolderPath);

    auto startTime = std::chrono::steady_clock::now();
    int totalFiles = 0, processedFiles = 0;
    std::vector<std::filesystem::path> filePaths;

    for (const auto& entry : std::filesystem::recursive_directory_iterator(inputFolderPath)) {
        if (!entry.is_regular_file()) continue;
        auto ext = entry.path().extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        if (ext == ".wav" || ext == ".ogg" || ext == ".opus" || ext == ".snd") {
            filePaths.push_back(entry.path());
            totalFiles++;
        }
    }

    // 分批处理的逻辑
    int numThreads = std::thread::hardware_concurrency();
    std::vector<std::thread> threads;
    size_t batchSize = filePaths.size() / numThreads;
    auto batchStartIt = filePaths.begin();

    for (int i = 0; i < numThreads; ++i) {
        auto batchEndIt = (i == numThreads - 1) ? filePaths.end() : batchStartIt + batchSize;
        std::vector<std::filesystem::path> batch(batchStartIt, batchEndIt);
        threads.emplace_back(processFilesBatch, batch, inputFolderPath, outputFolderPath, std::ref(processedFiles), totalFiles, startTime);
        batchStartIt = batchEndIt;
    }

    for (auto& t : threads) {
        t.join();
    }

    std::cout << std::endl << "Processing completed. " << processedFiles << "/" << totalFiles << " files processed." << std::endl;

    return 0;
}