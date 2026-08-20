import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (credentials?.email === "admin@testgen.ai" && credentials?.password === "admin") {
          return { id: "1", name: "Admin", email: "admin@testgen.ai" };
        }
        return null;
      }
    })
  ],
  pages: {
    signIn: '/api/auth/signin',
  }
});

export { handler as GET, handler as POST };