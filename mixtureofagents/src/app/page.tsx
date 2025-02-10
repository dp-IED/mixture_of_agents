"use client";

import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import Image from "next/image";
import { ArrowRight, FileUp, Brain, Workflow, FileOutput } from "lucide-react";
import WorkbenchLayout from '@/components/Workbench';

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [showWorkbench, setShowWorkbench] = useState(false);

  const handleSubmit = () => {
    if (!prompt.trim()) return;
    setShowWorkbench(true);
  };

  if (showWorkbench) {
    return <WorkbenchLayout prompt={prompt} />;
  }

  const features = [
    {
      icon: <FileUp className="w-6 h-6 text-blue-500" />,
      title: "Upload Your Data",
      description: "Import documents (PDF, DOCX, XLSX, CSV) or search history"
    },
    {
      icon: <Brain className="w-6 h-6 text-blue-500" />,
      title: "AI-Powered Analysis",
      description: "Our orchestrator assigns tasks to specialized agents"
    },
    {
      icon: <Workflow className="w-6 h-6 text-blue-500" />,
      title: "Watch Agents Work",
      description: "See real-time progress and agent collaboration"
    },
    {
      icon: <FileOutput className="w-6 h-6 text-blue-500" />,
      title: "Export Results",
      description: "Download as individual documents or unified summary"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-5xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <Image
            src="/logo.png"
            alt="SIMpol logo"
            width={400}
            height={60}
            priority
            className="mx-auto mb-8"
          />
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your AI-Powered Workbench
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Orchestrate AI agents to analyze, research, and create with your data
          </p>
          
          <div className="relative max-w-2xl mx-auto">
            <Input
              className="w-full h-12 pl-4 pr-12 text-lg shadow-lg border-none"
              placeholder="Start your journey with a prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key == 'Enter') handleSubmit();
              }}
            />
            <button className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 rounded-lg text-white hover:bg-blue-700 transition-colors">
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-blue-50 rounded-lg">
                  {feature.icon}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}