# RC-015: Optimistic UI Update Desynchronised From Server Response On Slow Network

## User Prompt

Our optimistic like counter occasionally flashes the wrong number before correcting itself on slow networks. How do we fix the race between optimistic updates and server responses?

## Context Provided To The Skill

- stack: React 18.2, TanStack Query 5.0, TypeScript 5.0
- environment: browser SPA on slow/mobile network
- logs:
- user likes a post — counter increments immediately (optimistic)
  - two rapid likes sent (double-tap)
  - server processes them out of order
  - final count shown: 2 above actual
  - server response arrives and overwrites with correct count
  - brief flash of wrong count visible
- code excerpt:
```js
const mutation = useMutation({
  mutationFn: likePost,
  onMutate: () => {
    queryClient.setQueryData(['post', id], old => ({
      ...old, likes: old.likes + 1  // optimistic — not rolled back on out-of-order response
    }))
  }
})
```
- reproduction:
1. Like a post twice rapidly on a throttled (3G) network
2. Observe like count briefly show wrong value
3. Server response corrects it with a visible flash
