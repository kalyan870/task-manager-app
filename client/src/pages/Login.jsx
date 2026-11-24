import { SignIn } from '@clerk/react';

export default function Login() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 bg-gradient-to-br from-indigo-50 to-blue-100 px-4 py-10">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-indigo-600">TaskManager</h1>
        <p className="mt-2 text-gray-600">Sign in to manage your tasks</p>
      </div>
      <SignIn routing="hash" signUpUrl="/register" forceRedirectUrl="/" />
    </main>
  );
}
