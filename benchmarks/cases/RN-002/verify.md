# Verification

## Before Fix
- Tapping Filter button causes 200 ProductCard re-renders (visible in Flipper profiler)
- Jank visible on physical device during any interaction

## After Fix
1. Add `keyExtractor={(item) => item.id.toString()}` to FlatList
2. Wrap renderItem: `const renderItem = useCallback(({ item }) => <ProductCard product={item} />, [])`
3. Wrap component: `const ProductCard = React.memo(function ProductCard({ product }) { ... })`
4. Tap Filter button → 0 ProductCard re-renders in profiler
5. Scrolling is smooth on physical device

## Regression Checks
- Adding a new item to products: only new item renders, existing items do not
- Removing an item: remaining items do not re-render
- Updating a single item's price: only that item re-renders
