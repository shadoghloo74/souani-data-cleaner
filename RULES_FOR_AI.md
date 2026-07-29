# 🛡️ Souani Technologies - AI Collaboration Rules

### 🚨 Strict Directives for AI Agents
1. **Scope Limit:** You are allowed to modify ONLY the explicitly specified module or function. Never refactor the entire codebase.
2. **UI Protection:** Never change the UI layout, color palette, or Tkinter themes unless explicitly requested.
3. **Core Engine:** DO NOT touch `engine.py` or core data processing logic unless the task is specifically about the cleaning engine.
4. **Compatibility:** Preserved backward compatibility is mandatory. Do not delete existing arguments, options, or methods.
5. **Tkinter Options:** Always use safe, standard `tkinter` / `ttk` properties (Avoid invalid options like `disabledbackground` on standard buttons).
6. **No File Deletion:** Never suggest deleting, renaming, or replacing files without explicit confirmation.
7. **Step-by-Step Delivery:** If code is large, split it logically without cutting off critical methods or classes.