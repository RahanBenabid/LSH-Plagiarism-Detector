import SwiftUI
import UniformTypeIdentifiers

// Define a struct to represent similarity results
struct SimilarityResult: Identifiable, Hashable {
    let docId: String
    let similarity: Double
    
    // Conform to Identifiable
    var id: String { docId }
}

struct ContentView: View {
    @State private var droppedText: String = "Drop your .txt file here"
    @State private var isTargeted: Bool = false
    @State private var isLoading: Bool = false
    @State private var similarityResults: [SimilarityResult] = []
    @State private var executionTime: Double = 0.0

    var body: some View {
        ZStack {
            VStack {
                Text(droppedText)
                    .font(.system(.body, design: .monospaced))
                    .padding()
                    .frame(width: 300, height: 150)
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
                        
                        Text(String(format: "Execution Time: %.3f seconds", executionTime))
                            .font(.subheadline)
                            .padding(.bottom)

                        // Modern Table implementation
                        Table(of: SimilarityResult.self) {
                            TableColumn("Document ID", value: \.docId)
                            TableColumn("Similarity %") { result in
                                Text(String(format: "%.2f", result.similarity))
                                    .foregroundColor(colorForSimilarityScore(result.similarity))
                            }
                        } rows: {
                            ForEach(similarityResults) { result in
                                TableRow(result)
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
            .blur(radius: isLoading ? 7 : 0)
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
                    
                    print("Failed to load drop:")
                    if let urlError = error {
                        print("URL error: \(urlError.localizedDescription)")
                    }
                    if let stringError = error {
                        print("String error: \(stringError.localizedDescription)")
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
                print("File reading error: \(error)")
            }
        }
    }
    ;
    private func sendTextToLocalhost(text: String) {
        // Reset previous results
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

                if let error = error {
                    print("Error sending text: \(error.localizedDescription)")
                    self.droppedText = "An error occurred while processing the file."
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse {
                    switch httpResponse.statusCode {
                    case 200:
                        // Process data as usual
                        if let data = data {
                            do {
                                let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]
                                
                                // Parse execution time as a Double
                                if let executionTime = json?["execution_time"] as? Double {
                                    self.executionTime = executionTime
                                } else if let executionTimeString = json?["execution_time"] as? String,
                                          let parsedTime = Double(executionTimeString) {
                                    self.executionTime = parsedTime
                                }
                                
                                // Parse similar documents
                                if let similarDocs = json?["similar_docs"] as? [String: Double] {
                                    self.similarityResults = similarDocs
                                        .map { SimilarityResult(docId: $0.key, similarity: $0.value) }
                                        .sorted { $0.similarity > $1.similarity }
                                }
                            } catch {
                                print("Error parsing JSON: \(error.localizedDescription)")
                            }
                        }
                    case 500:
                        // Handle 500 - No similar documents
                        self.droppedText = "No similar documents were found."
                    default:
                        // Handle other status codes
                        self.droppedText = "An unexpected server error occurred (Code: \(httpResponse.statusCode))."
                    }
                }
            }
        }.resume()
    }
}

#Preview {
    ContentView()
}
