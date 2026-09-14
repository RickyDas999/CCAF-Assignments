function SkeletonCard() {
  return (
    <div className="flex animate-pulse flex-col overflow-hidden rounded-xl border border-neutral-200 motion-reduce:animate-none dark:border-neutral-800">
      <div className="aspect-video w-full bg-neutral-100 dark:bg-neutral-800" />
      <div className="flex flex-col gap-2 p-4">
        <div className="h-4 w-4/5 rounded bg-neutral-100 dark:bg-neutral-800" />
        <div className="h-3 w-2/5 rounded bg-neutral-100 dark:bg-neutral-800" />
        <div className="h-3 w-full rounded bg-neutral-100 dark:bg-neutral-800" />
        <div className="h-3 w-3/5 rounded bg-neutral-100 dark:bg-neutral-800" />
      </div>
    </div>
  )
}

export default SkeletonCard
