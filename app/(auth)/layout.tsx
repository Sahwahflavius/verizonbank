export default async function RootLayout({
    children,
  }: Readonly<{
    children: React.ReactNode;
  }>) {
   
    return (
      <main className="flex h-screen w-full font-inter">
     {children}
      </main>
    );
  }