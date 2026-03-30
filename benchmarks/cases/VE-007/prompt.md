# VE-007: Breaking Change In Major Upgrade Not Documented In Migration Guide Causes Silent Data Loss

## User Prompt

After upgrading Mongoose from 6 to 7 some fields are not being updated correctly. Setting a field to null does not persist. No errors are thrown. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Mongoose 7.0 (upgraded from 6.x)
- environment: production after major version upgrade
- logs:
- no errors during save operations
  - fields with `null` value not being saved to MongoDB
  - was working correctly in Mongoose 6
  - affected fields have default values in schema
- code excerpt:
```js
const schema = new Schema({
  optionalNote: { type: String, default: null }
})
await Model.findByIdAndUpdate(id, { optionalNote: null })
```
- reproduction:
1. Upgrade Mongoose 6 to 7
2. Set a field to null via findByIdAndUpdate
3. Observe the field retains its old value instead of being set to null
