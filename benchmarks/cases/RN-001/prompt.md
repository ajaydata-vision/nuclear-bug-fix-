# RN-001: Metro Cannot Resolve Module After File Rename

## User Prompt

I renamed a component file from `UserCard.js` to `UserProfile.js` and updated every
import in the codebase. Metro now throws `Unable to resolve module './UserProfile'`
on the screen that imports it. The old filename `UserCard.js` no longer exists. I
have triple-checked every import statement — they all reference `UserProfile`. Deleting
`node_modules` and reinstalling did nothing. What is wrong?

## Context Provided To The Skill

- stack: React Native 0.73.4, Expo SDK 50, Metro 0.80.9
- versions: Node.js 20.11.0, macOS 14.3
- environment: development, `npx expo start`
- logs:
  - `error: Error: Unable to resolve module './UserProfile' from 'src/screens/HomeScreen.js'`
  - `None of these files exist: src/components/UserProfile(.js|.jsx|.ts|.tsx|/index...)`
  - `The module './UserProfile' could not be found`
- code excerpt:
```js
// HomeScreen.js — import already updated
import { UserProfile } from '../components/UserProfile';

// UserProfile.js — file exists at src/components/UserProfile.js
export function UserProfile({ user }) {
  return <View><Text>{user.name}</Text></View>;
}
```
- reproduction:
  1. Rename `UserCard.js` to `UserProfile.js`
  2. Update all imports to reference `UserProfile`
  3. `npx expo start` — error immediately on load
  4. File definitely exists: `ls src/components/UserProfile.js` returns the file
