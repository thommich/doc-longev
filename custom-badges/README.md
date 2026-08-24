# Docusaurus MDX badge component

This folder contains a dependency-free (apart from Docusaurus' existing `clsx`
dependency) badge component for Docusaurus 3.

## Install

Copy the included `src/components/Badge` directory into the same location in
your Docusaurus project.

In an MDX document, import and use it:

```mdx
import Badge from '@site/src/components/Badge';

The API is <Badge variant="success" pill>Stable</Badge>.
```

To make `<Badge>` available in every MDX file without imports, also copy
`src/theme/MDXComponents.tsx`. If your site already has that swizzle file, merge
the `Badge` import and property into its existing exported object instead of
replacing the file.

## Props

| Prop | Type | Default |
| --- | --- | --- |
| `variant` | `default \| info \| success \| warning \| danger \| purple` | `default` |
| `size` | `sm \| md \| lg` | `md` |
| `pill` | `boolean` | `false` |
| `dot` | `boolean` | `false` |
| `icon` | `ReactNode` | — |
| `className` | `string` | — |
| `style` | `CSSProperties` | — |

The component uses Docusaurus/Infima theme variables and includes dark-mode and
forced-color adjustments. `color-mix()` is supported in current evergreen
browsers; replace those declarations with fixed colors if supporting older
browsers is a requirement.
