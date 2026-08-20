import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, FileText, Zap, Globe } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-black text-white selection:bg-gray-800">
      <header className="px-6 lg:px-14 h-16 flex items-center border-b border-white/10">
        <Link className="flex items-center justify-center" href="/">
          <span className="font-bold text-xl tracking-tight">TestGen AI Pro</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6 items-center">
          <Link className="text-sm font-medium hover:text-gray-300 transition-colors" href="#features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:text-gray-300 transition-colors" href="#pricing">
            Pricing
          </Link>
          <Link href="/dashboard">
            <Button variant="secondary" className="bg-white text-black hover:bg-gray-200">
              Dashboard
            </Button>
          </Link>
        </nav>
      </header>
      <main className="flex-1">
        <section className="w-full py-24 lg:py-32 xl:py-48 flex justify-center text-center">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4">
              <div className="space-y-4 max-w-3xl">
                <h1 className="text-4xl font-extrabold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl/none bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">
                  The AI Question Paper Generator for Educators
                </h1>
                <p className="mx-auto max-w-[700px] text-gray-400 md:text-xl/relaxed lg:text-2xl/relaxed">
                  Upload a PDF. Get 20 questions in 10 seconds. Complete with source citations.
                  <br/>
                  <span className="text-white font-semibold">4 hours wasted. Solution: 60 seconds.</span>
                </p>
              </div>
              <div className="space-x-4 pt-4">
                <Link href="/dashboard">
                  <Button size="lg" className="bg-white text-black hover:bg-gray-200 h-12 px-8 font-medium">
                    Start Generating for Free
                  </Button>
                </Link>
              </div>
              <div className="pt-8 flex items-center gap-2 text-sm text-gray-500">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                Trusted by 5000+ Teachers
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="w-full py-20 bg-zinc-950 flex justify-center">
          <div className="container px-4 md:px-6">
            <div className="grid gap-12 lg:grid-cols-3">
              <div className="flex flex-col items-center space-y-4 text-center">
                <Zap className="h-10 w-10 text-white" />
                <h3 className="text-xl font-bold">Lightning Fast</h3>
                <p className="text-gray-400">Generate a full test in under 10 seconds using Google Gemini 1.5 Pro.</p>
              </div>
              <div className="flex flex-col items-center space-y-4 text-center">
                <FileText className="h-10 w-10 text-white" />
                <h3 className="text-xl font-bold">Source Citations</h3>
                <p className="text-gray-400">Every question comes with a direct citation from your uploaded PDF.</p>
              </div>
              <div className="flex flex-col items-center space-y-4 text-center">
                <Globe className="h-10 w-10 text-white" />
                <h3 className="text-xl font-bold">Workspaces</h3>
                <p className="text-gray-400">Create classes, organize tests, and share links easily.</p>
              </div>
            </div>
          </div>
        </section>

        <section id="pricing" className="w-full py-24 flex justify-center">
          <div className="container px-4 md:px-6 flex flex-col items-center text-center">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl mb-12">Simple, transparent pricing</h2>
            <Card className="w-full max-w-sm bg-zinc-900 border-zinc-800 text-white">
              <CardHeader>
                <CardTitle className="text-2xl">Pro Plan</CardTitle>
                <div className="text-4xl font-bold mt-4">$29<span className="text-lg font-normal text-gray-400">/mo</span></div>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-white" /> Unlimited PDFs</div>
                <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-white" /> 1-Click PDF/DOCX Export</div>
                <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-white" /> Advanced Analytics</div>
                <Button className="w-full mt-4 bg-white text-black hover:bg-gray-200">Subscribe Now</Button>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>
      <footer className="w-full py-6 flex justify-center border-t border-white/10 text-gray-500 text-sm">
        <p>© 2024 TestGen AI Pro. All rights reserved.</p>
      </footer>
    </div>
  );
}