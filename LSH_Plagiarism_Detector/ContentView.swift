//
//  ContentView.swift
//  LSH_Plagiarism_Detector
//
//  Created by Rahan Benabid on 11/12/2024.
//

import SwiftUI
import UniformTypeIdentifiers

struct ContentView: View {
    @State private var droppedText: String = "Drop your .txt file here"
    @State private var isTargeted: Bool = false

    var body: some View {
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

            Spacer()
        }
        .padding()
    }

    private func handleDrop(providers: [NSItemProvider]) -> Bool {
        for provider in providers {
            provider.loadObject(ofClass: URL.self) { (url, error) in
                if let url = url {
                    readFile(at: url)
                    return
                }
                
                provider.loadObject(ofClass: String.self) { (text, error) in
                    if let text = text {
                        DispatchQueue.main.async {
                            self.droppedText = text
                        }
                        return
                    }
                    
                    print("Failed to load drop: URL error - \(error?.localizedDescription ?? "Unknown")")
                    print("Failed to load drop: String error - \(error?.localizedDescription ?? "Unknown")")
                }
            }
        }
        return true
    }
    
    private func readFile(at url: URL) {
        do {
            let text = try String(contentsOf: url)
            DispatchQueue.main.async {
                self.droppedText = text
                
                // Commented out text sending functionality for later use
                /*
                sendTextToLocalhost(text: text)
                */
            }
        } catch {
            DispatchQueue.main.async {
                self.droppedText = "Failed to read file: \(error.localizedDescription)"
            }
        }
    }
    
    // Commented out function for sending text to localhost
    /*
    private func sendTextToLocalhost(text: String) {
        guard let url = URL(string: "http://127.0.0.1:5000") else {
            print("Invalid URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("text/plain", forHTTPHeaderField: "Content-Type")
        
        request.httpBody = text.data(using: .utf8)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error sending text: \(error.localizedDescription)")
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                print("Response status code: \(httpResponse.statusCode)")
            }
        }.resume()
    }
    */
}

#Preview {
    ContentView()
}
