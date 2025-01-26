export default async function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center">
      <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-[5rem]">
          GTD <span className="text-primary">App</span>
        </h1>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-8">
          <div className="flex flex-col gap-4 rounded-xl bg-white/10 p-4 hover:bg-white/20">
            <h3 className="text-2xl font-bold">Purpose →</h3>
            <div className="text-lg">
              Define your life purpose and core values
            </div>
          </div>
          <div className="flex flex-col gap-4 rounded-xl bg-white/10 p-4 hover:bg-white/20">
            <h3 className="text-2xl font-bold">Vision →</h3>
            <div className="text-lg">
              Set your long-term vision and outcomes
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
