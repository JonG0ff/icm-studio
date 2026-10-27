# Content Container Taxonomy

Use this in the destination workspace's brief when naming the content container.

## Platform

Use the user's platform if named. Common values:

- Instagram
- TikTok
- YouTube
- LinkedIn
- Facebook
- X
- Email
- Website
- Other
- Unknown

## Placement Or Post Type

Use the most specific term the user gives.

| Platform | Common placements |
|----------|-------------------|
| Instagram | Reel, Story, Feed post, Carousel, Static post, Ad |
| TikTok | TikTok video, Spark ad, Story, Photo carousel |
| YouTube | Short, Video, Community post, Thumbnail |
| LinkedIn | Post, Carousel, Article, Newsletter, Ad |
| Facebook | Feed post, Reel, Story, Group post, Ad |
| X | Post, Thread, Video post |
| Email | Broadcast, Sequence email, Newsletter |
| Website | Blog post, Landing page, Case study |

## Output Intent

Map platform and post type to the deliverable the owning workspace will produce.

| Output intent | Use when |
|---------------|----------|
| `short-form-video` | Instagram Reel, TikTok video, YouTube Short, vertical social video |
| `split-test-cell` | A set of reel variants built to answer one question, published one per day as trial reels |
| `carousel` | Instagram carousel, LinkedIn carousel, PDF carousel |
| `copy-only` | Caption, LinkedIn post, X post, email, text-only social post |
| `long-form-video` | Chaptered tutorial, interview, demonstration, or other longer video |
| `narrated-video` | Narrated video; choose Video Production or Programmatic Animation based on the production method |
| `course-deck` | Slide deck, course deck, workshop deck |
| `image-post` | Static image, quote card, thumbnail, graphic post |
| `other` | Anything that does not fit the list |
| `unknown` | The user has not named the content type yet |

## Required Container Fields

- `platform`
- `placement_or_post_type`
- `output_intent`
- `orientation_or_shape` when known
- `target_length_or_size` when known
- `publishing_context` when known

Do not invent platform-specific specs. The owning workspace sets production requirements in its brief.

Use `split-test-cell` when the idea is meant to be tested rather than published once. Video Production owns it and produces several variants from one idea. If the user only wants one reel, use `short-form-video`.
