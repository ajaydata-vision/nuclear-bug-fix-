# RN-002: FlatList Re-Renders Every Item On Any Parent State Change

## User Prompt

Our product list screen has a FlatList with 200 items. Any interaction — tapping
a filter button, toggling a modal, updating an unrelated counter — causes massive
jank. Profiling shows all 200 items re-rendering simultaneously even when the list
data has not changed. The items are simple cards, nothing expensive. Why is everything
re-rendering?

## Context Provided To The Skill

- stack: React Native 0.73.6, React 18.2.0, TypeScript 5.3
- versions: Expo SDK 50, Flipper 0.212.0
- environment: iOS simulator and physical device, release and debug builds
- logs:
  - Flipper Profiler: 200 `ProductCard` renders fire simultaneously on every button press
  - No console errors
- code excerpt:
```tsx
// ProductListScreen.tsx
export function ProductListScreen() {
  const [filterOpen, setFilterOpen] = useState(false);
  const products = useProductStore(state => state.products);

  return (
    <>
      <Button onPress={() => setFilterOpen(true)} title="Filter" />
      <FlatList
        data={products}
        renderItem={({ item }) => <ProductCard product={item} />}
        // no keyExtractor
      />
      {filterOpen && <FilterModal onClose={() => setFilterOpen(false)} />}
    </>
  );
}

function ProductCard({ product }: { product: Product }) {
  return (
    <View style={styles.card}>
      <Text>{product.name}</Text>
      <Text>${product.price}</Text>
    </View>
  );
}
```
- reproduction:
  1. Open ProductListScreen with 200 items
  2. Tap the Filter button (does not change products array)
  3. Profiler shows all 200 ProductCard components re-render
