# MO-004: App Crash On Low Memory Because Large Bitmaps Not Recycled

## User Prompt

Our image gallery crashes on lower-end Android devices with OutOfMemoryError when scrolling through photos. High-end devices are fine. What is causing the crash?

## Context Provided To The Skill

- stack: React Native 0.73, react-native-fast-image 8.6
- environment: Android devices with limited RAM (2-3GB)
- logs:
- java.lang.OutOfMemoryError: Failed to allocate bitmap
  - crash occurs in image-heavy list views
  - only affects Android devices with less than 4GB RAM
  - crash frequency increases with scroll depth
- code excerpt:
```jsx
<FlatList
  data={photos}
  renderItem={({ item }) => (
    <Image source={{ uri: item.url }} style={{ width: 800, height: 600 }} />
  )}
/>
```
- reproduction:
1. Open image gallery on a 3GB Android device
2. Scroll quickly through large list
3. App crashes with OutOfMemoryError
