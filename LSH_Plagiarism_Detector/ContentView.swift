import SwiftUI
import UniformTypeIdentifiers

// Define a struct to represent similarity results
struct SimilarityResult: Identifiable, Hashable {
    let docId: String
    let similarity: Double
    
    // Conform to Identifiable
    var id: String { docId }
}

// A new view to display the file content
struct FileContentView: View {
    let fileName: String
    let fileContent: String
    let originalText: String  // New parameter
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("File: \(fileName)")
                .font(.title)
                .fontWeight(.bold)
                .padding(.top)
            
            Divider()
            
            // Original Text Section
            VStack(alignment: .leading, spacing: 8) {
                Text("Original Text")
                    .font(.headline)
                    .fontWeight(.semibold) // Ensures boldness matches the "File" style
                    .font(.system(.body, design: .monospaced))
                
                ScrollView {
                    Text(originalText)
                        .font(.system(.body, design: .monospaced))
                        .multilineTextAlignment(.leading)
                        .padding()
                }
                .frame(maxHeight: 200)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(10)
            }
            .padding(.bottom)
            
            // File Content Section (Modified to match "Original Text" style)
            VStack(alignment: .leading, spacing: 8) {
                Text("File Content")
                    .font(.headline)
                    .fontWeight(.semibold) // Ensures consistent boldness
                    .font(.system(.body, design: .monospaced))
                
                ScrollView {
                    Text(fileContent)
                        .font(.system(.body, design: .monospaced))
                        .multilineTextAlignment(.leading)
                        .padding()
                }
                .frame(maxHeight: 200)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(10)
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("File Viewer")
    }
}

enum NavigationRoute: Hashable {
    case fileContent(fileName: String, fileContent: String, originalText: String)
}

struct ContentView: View {
    @State private var droppedText: String = "Drop your .txt file here"
    @State private var isTargeted: Bool = false
    @State private var isLoading: Bool = false
    @State private var similarityResults: [SimilarityResult] = []
    @State private var executionTime: Double = 0.0
    @State private var selectedFileName: String = ""
    
    @State private var fileContent: String = ""  // Stores file content
    @State private var originalDroppedText: String = ""  // Store original text
    @State private var navigationRoute: NavigationRoute?
    
    var body: some View {
        NavigationStack {
            ZStack {
                VStack {
                    // Drop Area
                    Text(droppedText)
                        .font(.system(.body, design: .monospaced))
                        .padding()
                        .frame(width: 500, height: 200)
                        .background(isTargeted ? Color.yellow : Color.gray.opacity(0.2))
                        .cornerRadius(10)
                        .onDrop(of: [.fileURL, .text, .utf8PlainText], isTargeted: $isTargeted) { providers in
                            handleDrop(providers: providers)
                        }
                        .animation(.default, value: isTargeted)

                    // Results Table
                    if !similarityResults.isEmpty {
                        VStack {
                            Text("Similarity Results")
                                .font(.headline)
                                .padding()
                            
                            Text(String(format: "Execution Time: %.3f seconds", executionTime))
                                .font(.subheadline)
                                .padding(.bottom)

                            Table(of: SimilarityResult.self) {
                                TableColumn("Document ID", value: \.docId)
                                TableColumn("Similarity %") { result in
                                    Text(String(format: "%.2f", result.similarity))
                                        .foregroundColor(colorForSimilarityScore(result.similarity))
                                }
                            } rows: {
                                ForEach(similarityResults) { result in
                                    TableRow(result)
                                        .contextMenu {
                                            Button("Show File") {
                                                let modifiedFileName = mapFileName(result.docId)
                                                fetchFileContent(fileName: modifiedFileName)
                                            }
                                        }
                                }
                            }
                            .frame(minHeight: 200, maxHeight: 300)
                            .padding()
                        }
                        .padding()
                    }

                    Spacer()
                }
                .padding()
                .blur(radius: isLoading ? 7 : 0) // Blur the content when loading
                .disabled(isLoading)

                // Loading overlay
                if isLoading {
                    Color.black.opacity(0.3)
                        .edgesIgnoringSafeArea(.all)
                        .overlay(
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle())
                                .scaleEffect(1.5)
                        )
                }
            }
            .background(
                Color.white.opacity(0.3)  // Apply a translucent background
                    .blur(radius: 10)  // Apply a blur effect
            )
            .navigationDestination(item: $navigationRoute) { route in
                switch route {
                case .fileContent(let fileName, let fileContent, let originalText):
                    FileContentView(
                        fileName: fileName,
                        fileContent: fileContent,
                        originalText: originalText
                    )
                }
            }
        }
    }

    // Map doc ID (e.g., "doc_1.txt") to "essay1.txt"
    private func mapFileName(_ docId: String) -> String {
        if docId.starts(with: "doc_") {
            let number = docId.dropFirst(4) // Extract the number (e.g., "1")
            return "essay\(number).txt"
        }
        return docId
    }

    private func fetchFileContent(fileName: String) {
        // Build the URL with query parameters
        var components = URLComponents(string: "http://127.0.0.1:5000/read")
        components?.queryItems = [
            URLQueryItem(name: "name", value: fileName)
        ]
        
        guard let url = components?.url else {
            print("Invalid URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json; charset=utf-8", forHTTPHeaderField: "Content-Type")
        request.setValue("close", forHTTPHeaderField: "Connection")

        // Execute the GET request
        isLoading = true
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                if let error = error {
                    print("Error: \(error.localizedDescription)")
                    return
                }
                if let data = data,
                   let jsonResponse = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let content = jsonResponse["file_content"] as? String {
                    
                    self.selectedFileName = fileName
                    self.fileContent = content
                    self.navigationRoute = .fileContent(
                        fileName: fileName,
                        fileContent: content,
                        originalText: originalDroppedText
                    )
                } else {
                    print("Invalid response or no data")
                }
            }
        }.resume()
    }

    private func colorForSimilarityScore(_ score: Double) -> Color {
        switch score {
        case 0.9...1.0:
            return .red
        case 0.7..<0.9:
            return .orange
        case 0.6..<0.7:
            return .yellow
        default:
            return .green
        }
    }
    
    private func handleDrop(providers: [NSItemProvider]) -> Bool {
        guard !providers.isEmpty else { return false }
        
        let group = DispatchGroup()
        
        for provider in providers {
            group.enter()
            
            provider.loadObject(ofClass: URL.self) { (url, error) in
                defer { group.leave() }
                
                if let url = url {
                    DispatchQueue.main.async {
                        self.readFile(at: url)
                    }
                    return
                }
                
                provider.loadObject(ofClass: String.self) { (text, error) in
                    if let text = text {
                        DispatchQueue.main.async {
                            self.droppedText = text
                            self.sendTextToLocalhost(text: text)
                        }
                        return
                    }
                }
            }
        }
        return true
    }
    
    private func readFile(at url: URL) {
        DispatchQueue.main.async {
            do {
                guard url.isFileURL else {
                    self.droppedText = "Invalid file URL"
                    return
                }
                
                let text = try String(contentsOf: url, encoding: .utf8)
                self.droppedText = text
                self.sendTextToLocalhost(text: text)
            } catch {
                self.droppedText = "Failed to read file: \(error.localizedDescription)"
            }
        }
    }

    private func sendTextToLocalhost(text: String) {
        self.originalDroppedText = text  // Store the original text
        self.similarityResults.removeAll()
        self.isLoading = true

        guard let url = URL(string: "http://127.0.0.1:5000/replace") else {
            print("Invalid URL")
            self.isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonBody = ["text": text]
        request.httpBody = try? JSONEncoder().encode(jsonBody)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                self.isLoading = false

                if let data = data {
                    do {
                        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                        
                        if let executionTime = json?["execution_time"] as? Double {
                            self.executionTime = executionTime
                        }
                        
                        if let similarDocs = json?["similar_docs"] as? [String: Double] {
                            self.similarityResults = similarDocs
                                .map { SimilarityResult(docId: $0.key, similarity: $0.value) }
                                .sorted { $0.similarity > $1.similarity }
                        }
                    } catch {
                        print("Error parsing JSON: \(error.localizedDescription)")
                    }
                }
            }
        }.resume()
    }
}

#Preview {
    ContentView()
}
