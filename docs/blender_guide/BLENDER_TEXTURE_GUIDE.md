### Comprehensive Guide for Adding and Baking Textures from BlenderKit Materials

This guide is a complete, self-contained reference for extracting usable PNG textures (color/diffuse maps and normal maps) from BlenderKit materials, tailored for your voxel-based mining app in Three.js. It's based on our iterative process, where we started with basic baking but refined for issues like black/blank outputs, low contrast, artifacts (e.g., stripes from Voronoi flattening), and performance (e.g., GPU acceleration to avoid long waits). We ended up favoring Emission bakes for color (pure procedural capture without lighting washout) and Normal bakes for depth, as these balance realism with low compute in your app.

- **Why this approach?** Baking flattens 3D procedurals into 2D PNGs, losing viewport effects like real-time lighting/displacement. We use temporary Emission to preserve patterns, and normals to "fake" back depth in the app without extra geometry (efficient for many small voxels ~80px). This thinking prioritizes tileability (seamless repeats on cube faces) and scalability (higher-res bakes that GPU mip-maps for sharpness).

For other minerals, categorize based on type:
- **Procedural (e.g., quartz, mica—Voronoi/noise-based)**: Follow full guide; scale low (5-15) for macro veins, emphasize Emission to avoid flatness.
- **PBR/Image-Based (e.g., basalt, granite—pre-loaded textures)**: Simpler—skip procedural tweaks; bake directly if needed, or export images from nodes without Emission (faster, higher fidelity).
- **Metallic/Gem (e.g., gold, emerald—shiny/reflective)**: Add metalness/roughness bakes (type: Roughness/Metallic); in app, boost emissive for glow.
- **Organic (e.g., coal, limestone—rough/porous)**: Higher Voronoi randomness (0.8+); bake with slight displacement for normals, but keep low to avoid artifacts on small voxels.

Prerequisites: Blender 5.0+, BlenderKit add-on enabled. (Blender 3.0 will work but instructions may vary). Free HDRI downloaded (e.g., from Poly Haven for even lighting—place in an easy folder like /tmp).

#### Step 1: Enable GPU and Optimize Render (For Fast Bakes)
- Edit > Preferences > System > Cycles Render Devices: select CUDA (NVIDIA) or OptiX (newer NVIDIA) if available, or HIP (AMD). Check your GPU box. If you get error unable to select GPU restart your computer.
- Render Properties (camera icon in the vertical tabs on the right side): Render Engine > Cycles; Device: GPU Compute; Render > Samples Min 64, Max 128; Denoising > OpenImageDenoise.
- Restart Blender.
  - **Why first?** GPU setup often requires restart for full effect; doing it early avoids resaving/reopening projects mid-process if you forget. If no restart prompt, it may apply immediately, but restarting ensures stability.  
  - **Thinking**: GPU cuts bake time from hours to seconds—critical for iteration. Lower samples test fast; increase for noise-free details. For organic minerals (coal), higher max (256) captures porous textures better.

#### Step 2: Add and Prepare the Plane (Canvas for Baking)
- Hide/remove the default cube from Scene Selection.
- In 3D Viewport: Add > Mesh > Plane.
- Orient camera from top down by clicking Z in the axis key (number pad 7).
- Scale for pattern capture: Select plane > Press S > Type 4 > Enter (uniform scale; ~8x8 units).
  - **Why?** Larger captures broader procedural details (e.g., fewer repetitive cells in quartz Voronoi) without over-detailing small app voxels. For other minerals like basalt (textured), scale 2-3 if patterns are finer.
- UV Unwrap: Edit Mode (Tab) > U > Smart UV Project > Unwrap (default settings). Back to Object Mode (Tab). (How to confirm that the Smart UV Project was applied? Click on Plane in the Scene Collection > Select Properties tab from the top of the vertical toolbar on the right side > Data (green triangle) > UV Maps > Look for a UVMap in the list, if's empty you need to add it still).
  - **Thinking**: UVs ensure flat, distortion-free mapping—essential for tileable PNGs in your app (avoids seams on cube edges).

#### Step 3: Search and Assign the Material
- Select the "Shading" tab in the main tabs at the top of the screen.
- Sidebar (N key) > BlenderKit tab: Select "Materials", Type search term (e.g., "Quartz") > Choose and Drag to plane. Note: You can also browse on Blenders website and copy/paste the asset code.
- Preview: Viewport shading > Material Preview or Rendered. 
  - **Why drag?** Applies instantly; for PBR minerals (e.g., granite), check nodes for pre-loaded images—simpler than procedurals.

#### Step 4: Set Up HDRI Lighting (For Better Contrast in Bakes)
- Shader Editor > World mode (dropdown).
- Chain: Shift+A > Texture > Environment Texture > Place at start of chain
- Load HDRI: Open > docs/studio_small_08_4k.exr or download from [Polyhaven](https://polyhaven.com/hdris))
- Chain: Environment Texture Color to Background Color (add Background if missing: Shift+A > Shader > Background) > Background to World Output Surface.
- Background Strength: 1.5.
  - **Why?** HDRI provides even, realistic light without harsh shadows—boosts procedural contrast (e.g., quartz veins pop more). For metallic minerals (gold), use brighter HDRIs like "venice_sunset" for sparkle. Skip for pure grayscale bakes if overkill.
![World shader example](docs/blender_texture_export_shading_proc_chain_setup_world.png)

#### Step 5: Create Bake Targets (For Color and Normal Maps)
- The procedural chain for the Object (your assigned material like Simple Quartz) will vary depending on the material/BlenderKit asset—some are simple (e.g., single Voronoi for patterns), others complex (e.g., multiple BSDFs/Mixes for glass-like effects). This is expected, as creators design unique setups for realism. Leave it as-is initially; we'll adjust temporarily in later steps for baking.
- Shader Editor (Object mode): Shift+A > Texture > Image Texture (Don't connect to procedural chain) > New (Name "Quartz_Color", 512x512, Color:no change, Generated Type:Blank, don't check any of alpha/32-bit/tiled, Confirm New Image, check that Color Space:sRGB).
- Duplicate (Shift+D) for "Quartz_Normal" (identical).
  - **Why duplicate?** Keeps settings consistent without overwriting—color for visible patterns, normal for bumps. For gems (emerald), use 1024+ res for sharp facets (bake time may take longer).
![Bake Targets Example](docs/bake_targets_example.png)

#### Step 6: Bake the Normal Map (Bumps/Depth)
- No chain changes (use full original—keeps displacement for grooves).
  - In the case of a procedural mineral texture () then we can make the output more tileable by following the guide below "Quick Node Setup for Tileable Voronoi""
- Render Properties (camera icon in vertical toolbar) > Bake > Bake Type:Normal; Space:Tangent; Max Ray Distance 0.2 (Check 'Selected to active', change value then uncheck it); Clear Image checked;  Margin Size 32px.
  - **Why Normal?** Encodes grooves (colorful RGB data—teal/pink fine, not visible in app) for fake 3D in your voxels. For smooth minerals (mica), lower Displacement first to soften.
- Orient camera from top down by clicking Z in the axis key (number pad 7).
- Select plane and "Simple_Quartz" node > Bake. Check the Long FAQ > Errors section below if errors occur.
- Check the preview in the Image Editor. In the case of quartz we will be changing the voronoi scaling until there are 4-6 features in the resulting baked image, where a feature is a distinct, visible element in the pattern, such as a single polygonal cell (e.g., an irregular square, trapezoid, or triangle formed by the Voronoi divisions) or a vein/cluster group. It's not just an evaluated vertex (point where edges meet)—think of it as the full shape bounded by edges, including how edges connect to form the geometry. For 4-6 features, aim for 4-6 clear cells or vein segments in the PNG—ensuring the image isn't too crowded (many tiny shapes blur on small voxels) or sparse (few large blobs look flat). This balances macro mining realism (broad crystals) with detail.
Preview in the Image Editor after each adjustment to confirm tileability and contrast—aim for a balance where the pattern repeats seamlessly without looking overly repetitive or flat.
To check tileability (seamless repeating without visible edges when tiled): Go to the preview in the Image Editor > View > Repeat Image 
Zoom in on the seams where the edges meet. If there's no noticeable mismatch, discontinuity, or hard line (the pattern flows naturally across boundaries), it's tileable.

- Image Editor > Select "Simple_Quartz" > Image > Save As
  - [x] Save as Render. Check this. Why? It applies the viewport's color management (e.g., sRGB transform) to the PNG, making it look closer to what you see in the Image Editor preview (with proper contrast/tones). Unchecked saves raw data, which might appear washed out/dark in external viewers or your app.
  - [] Copy. Uncheck this. Why? It saves the image as a new file without overwriting the in-memory buffer—unnecessary here, as you're exporting for app use, not keeping multiples in Blender.
  - [] Relative Path. Uncheck this (or ignore; it's grayed out for absolute saves). Why? It's for linking paths in .blend files (e.g., project portability)—irrelevant for standalone PNG exports to your app's /textures/ folder.
  - Media Type (File Format): Image (PNG). Why? PNG is a standard, lossless format for textures—supports compression without quality loss. Avoid Multilayer EXR (for HDR/float/multi-channel data like OpenEXR workflows); it's overkill, larger files, and not needed for your app's simple color/normal maps.
  - Color: RGB. Why? Your bakes are opaque (no transparency), so RGB (red/green/blue) is sufficient—saves space vs. RGBA (adds alpha channel). Normal maps use RGB to encode directions (red=X, green=Y, blue=Z), and color maps don't need alpha for minerals.
  - Color Depth: 8. Why? Standard for web/3D apps—balances quality/file size (256 colors per channel). 16-bit (65k colors) adds precision but bloats files (2x size) with minimal benefit for your small voxels (~80px); use only if high dynamic range is needed (rare for quartz-like procedurals).
  - Compression %: Default 15% is fine, or increase to 50-70% if files are large. Why? Higher % = more compression/smaller PNGs with minor quality loss (negligible for textures). Keep lower (15-30%) for detailed patterns to avoid artifacts; test in app—your GPU handles compressed PNGs efficiently.
  - Overrides for Color Management: Leave optional/defaults (e.g., View Transform: Standard, Look: None). Why? They're for advanced overrides (e.g., filmic grading)—unnecessary here, as "Save as Render" already applies sRGB-like transforms for consistent app previews. If your PNG looks off in external viewers, enable Filmic for higher contrast, but test.
  - Filename: add '_normal' to the end of the filename and save to the repository lithos_explore/frontend/public/textures/simple_quartz_normal.png
  - Check the saved Image. The saved PNG should closely match the Image Editor preview (after baking), but flatter/duller than the full 3D Viewport render (which includes real-time lights/displacement). It's not plain black (if bake succeeded)—black indicates errors like wrong chain/reroute. Save as Render helps align it to preview.
    - For Normal Bake (Normal): Abstract, colorful (teal/pink/red/blue gradients encoding bumps—e.g., cell edges as color shifts). Not "natural" like preview (it's data, not a photo)—won't match 3D shading, but adds depth in app. If black/flat, ensure full chain (with displacement) and Tangent Space.

Example with 8-12 features (Simple_Quartz_scale15.2_8to12features.png)  Reduce Voronoi scaling so we get around 4-6 features so it looks like 

- **You should not** change any settings like Voronoi scale (or other procedural parameters such as randomness, feature weights, or displacement) between the normal and color bakes. If you do, the resulting maps won't align properly, leading to visual mismatches in your app (e.g., bumps/grooves in the normal map offset from the patterns/veins in the color map, causing artifacts like floating shadows or misaligned details on voxels).

- See FAQ/Tips section below for common issues like stuck at 0%, black bake, and advice on iterating settings like voronoi.
![Normal Map Example](docs/blender_example_simple_quartz_baketype_normal.png)

What to Expect the PNG to Look Like - The saved PNG should closely match the Image Editor preview (after baking), but flatter/duller than the full 3D Viewport render
- For Normal Bake (Normal): Abstract, colorful (teal/pink/red/blue gradients encoding bumps—e.g., cell edges as color shifts). Not "natural" like preview (it's data, not a photo)—won't match 3D shading, but adds depth in app. If black/flat, ensure full chain (with displacement) and Tangent Space.

#### Step 7: Bake the Color Texture (Visible Patterns)
- Temporary Chain Changes: Add Shift+A > Shader > Emission. Trace the chain to find a yellow Color output (e.g., from Voronoi Color, Color Ramp Color, or Mix RGB Result—often unused or early in path). Connect that to Emission color > Emission output to Material Output Surface (bypass final shaders like Principled BSDF or Mix Shader—note original connections to revert). If no yellow, add Mix (Shift+A > Color > Mix, set to Color mode) to blend grays/vectors into color before Emission.
  - **Why Emission?** Captures raw procedural (Voronoi shapes) without lighting washout—avoids dark/flat. For image-based minerals (basalt), skip this; bake directly.
- Bake Properties: Type > Emission; Uncheck all Influence; Margin Type Adjacent Faces; Same settings as normal.
- Select plane and "Quartz_Color" node > Bake.
- Image Editor > Select "Simple_Quartz" > Image > Save As > Same settings as before. Add '_em' to the end of the filename and save to the repository lithos_explore/frontend/public/textures/simple_quartz_color.png
  - Check the saved Image. For Color Bake (Emission): A grayscale or tinted pattern replicating the procedural shapes (e.g., 4-6 Voronoi cells/veins for quartz—subtle edges, medium contrast). Not as "nice" as 3D preview (no shadows/glow), but vibrant/not flat. If black, check Emission reroute (connect yellow Color output properly).

![Color Bake example](docs/blender_example_simple_quartz_baketype_color.png)


What to Expect the PNG to Look Like - Color Bake (Emission): A grayscale or tinted pattern replicating the procedural shapes (e.g., 4-6 Voronoi cells/veins for quartz—subtle edges, medium contrast). Not as "nice" as 3D preview (no shadows/glow), but vibrant/not flat. If black, check Emission reroute (connect yellow Color output properly).
- Blurry? gradient-like blurriness is likely not a critical problem - common with procedural materials like Simple Quartz, where the Voronoi-based patterns (cells/edges) are designed to blend smoothly via gradients (from Color Ramp/Mix nodes) rather than sharp lines. This isn't "true" blur (e.g., from low res or denoising artifacts) but an intentional soft transition for realism (mimicking natural quartz diffusion). It wasn't blurry initially in the 3D Viewport because previews include dynamic lighting/displacement (adding perceived sharpness via shadows/highlights), which baking flattens to 2D—losing that "pop."
  - When to Worry: If too washed-out (losing veins/detail), it's suboptimal for education (e.g., quartz crystals blur into gray mush). Fix for sharpness if planning close-ups/orbits.

  - Ways to Make It Less Blurry/Gradient (Without Re-Baking Everything)
    - In Blender (Quick Tweaks):
      - Color Ramp: Add sharper stops (e.g., position 0: dark gray, 0.4: mid gray, 0.6: light gray, 1.0: white)—set Interpolation to Constant (hard edges) or Linear (less gradient). Re-bake color.
      - Voronoi: Increase Intensity (1.5-2.0) for contrast; lower Scale (5-10) for fewer/bolder features (reduces "blurry" density). Re-bake both if scale changes (to match normals).
      - Post-Compositor: In Compositing workspace > Use Nodes > Add Image (your color PNG) > Filter > Sharpen (factor 1.5-2.0) > Output. Render (F12) > Save new PNG. This crisps without external editors.

    - In App (Three.js Fixes):
      - Material: Add texture.magFilter = THREE.LinearFilter; (sharper magnification on small voxels). Or texture.anisotropy = 16; (anti-alias angles, reduces perceived blur).
      - Normal Boost: If using normal map, increase normalScale={new THREE.Vector2(1.0, 1.0)}—adds edge definition via fake shadows, countering gradients.
      - Test Tiling: Set repeat.set(1,1) for full image per face (less "stretched" blur); if good on partial, commit it.
  
#### Step 8: Test PNGs in App
- lighting/normalScale revives 3D look. If underwhelming, iterate Voronoi (scale/randomness) before rebaking.


#### App Integration
- In `Explorer3D.js`: Expand `textures` (color) and `normalMaps` (normals) with loaders.
- Material: `map={textures[type]}; normalMap={normalMaps[type]}; normalScale={new THREE.Vector2(0.5, 0.5)};` (adjust scale for bump strength).
- Tiling: `texture.repeat.set(1,1);` (full per face) or 2,2 (more detail).
  - **Consideration**: For macro world, low Voronoi scale + repeat 1 avoids clutter. Test on 80px voxels.

#### FAQ/Tips
- **Voronoi Settings**: Dimension 3D; Feature Cells; Scale 5-15 (low for macro veins); Randomness 0.8. For gems (diamond), higher scale (20) for fine facets.
- **Stuck Bake (0%)**: Lower samples; ensure GPU. If cancels but produces image, it's partial—increase Max Samples for full detail.
- **Dark/Flat Bake**: Use Emission for color; HDRI Strength 1.5. If low detail, higher res (1024x1024) or Voronoi Scale.
- **Artifacts**: Lower Displacement 0.05; use Denoising.
- **Performance**: 512x512 PNGs light; normals add depth without cost.
- **Other Minerals**: Procedurals need Emission tweaks; PBR skip temporary chains—bake direct.

#### Terminology Section
This section explains key terms used in the guide, for users unfamiliar with 3D modeling/Blender. Terms are categorized for clarity, with simple definitions and why they're relevant to your app. We've included everything you might reasonably run into within our scope, such as PBR (Physically Based Rendering), which was excluded initially but is now added as it's central to realistic material baking and app integration (e.g., for metallic minerals like gold).

**General 3D Concepts**:
- **Bake/Baking**: Rendering a material's effects (e.g., patterns, lighting) into a 2D image file (PNG). Flattens complex procedurals for efficient use in apps like yours—saves compute by pre-computing details.
- **HDRI (High Dynamic Range Image)**: 360° environment map for lighting (e.g., studio HDR). Provides realistic, even illumination in bakes, enhancing contrast without manual lights—makes minerals look "poppy" in previews.
- **Material**: Collection of properties (color, shine, bumps) defining an object's look. Your BlenderKit quartz is a material; baking extracts its textures for voxels.
- **Node (in Shader Editor)**: Building block for materials (e.g., Voronoi node generates patterns). Chains like yours create procedurals—adjust to control detail without code.
- **PBR (Physically Based Rendering)**: Shading model simulating real-world light (e.g., metalness/roughness maps). Many BlenderKit assets are PBR—baking them gives app-ready textures with realistic shine/bumps for minerals like emerald.
- **Procedural**: Algorithm-generated texture (e.g., Voronoi math creates veins). Why? Infinite variety, but needs baking for app export—scales better than hand-painted for mining worlds.
- **UV Unwrap/UV Mapping**: "Flattening" a 3D surface to 2D coordinates for textures. Ensures patterns apply without distortion on your cube faces—like unfolding a box for wrapping paper.

**Blender-Specific Terms**:
- **3D Viewport**: Main window showing your 3D scene (e.g., plane). Why? Where you add/scale objects—preview here before baking.
- **Shader Editor**: Window for building material nodes (e.g., connecting Voronoi to Emission). Why? Core for tweaking/baking procedurals like quartz—switch modes (Object/World) for different chains.
- **Render Properties**: Tab (camera icon) for bake settings (e.g., Type: Emission). Why? Controls quality/speed—Cycles engine + GPU makes bakes fast for iteration.
- **Image Editor**: Window for viewing/saving baked PNGs. Why? Final check/export step—ensures no black/blank issues.

**App-Relevant Terms (Three.js Integration)**:
- **Color Texture (Diffuse Map)**: Visible PNG (grayscale patterns). Why? Base look for voxels—tints with MINERAL_COLORS for hue.
- **Normal Map**: Colorful RGB PNG encoding bumps. Why? Adds fake depth (grooves/shadows) without extra compute—makes flat voxels 3D-like under lights.
- **Tiling/Repeat**: How textures wrap/repeat on surfaces. Why? Set low (1,1) for full image per face (no seams); higher (2,2) adds detail for macro views.

##### Long FAQ
###### Known Errors
  - "Uninitialized Image 'Simple Quartz' from object 'Plane'" in Blender typically occurs when the target Image Texture node has an assigned image name/datablock, but the image itself lacks data (e.g., it's not properly created, loaded, or initialized in memory). This can happen from node duplication without re-creating the image, unsaved changes, or Blender glitches like corrupted buffers. It doesn't mean your configuration is wrong—just that the image target isn't "filled" yet. Since you didn't change anything, it's likely a state issue from previous bakes.
    Quick Fixes (Try in Order)
    
    - Re-Create the Image in the Node:
    - In Shader Editor, select the problematic Image Texture node (e.g., "Quartz_Color" or "Quartz_Normal").
    - Click the X next to the image name (clears the datablock).
    - Click New > Re-enter settings (e.g., Name "Quartz_Color", 512x512, Blank, sRGB).
    - This reinitializes—bake again.
    
    - Clear and Re-Bake:
    - In Bake Properties: Check Clear Image (forces overwrite of buffer).
    - Select plane/node > Bake. If stuck, lower samples (Min 32, Max 64) to test.
    
    - Restart or Reload:
    - Save .blend file > Close/reopen Blender (clears memory glitches).
    - Or File > New > Reload Startup File (resets without closing).
    
    - If Persists (Rare):
    - Check Outliner > Datablocks > Images—delete orphaned "Simple Quartz" if listed (right-click > Delete).
    - Ensure no hidden objects/layers interfere (View > Show Hidden).
    
    - This should resolve it without redoing steps—test a small bake (512x512) first. If error changes, note the exact message for more help.


- you should not change any settings like Voronoi scale (or other procedural parameters such as randomness, feature weights, or displacement) between the normal and color bakes. If you do, the resulting maps won't align properly, leading to visual mismatches in your app (e.g., bumps/grooves in the normal map offset from the patterns/veins in the color map, causing artifacts like floating shadows or misaligned details on voxels).
  - Why This Matters
    - Alignment Requirement: The normal map encodes 3D depth based on the material's surface (including procedural shapes from Voronoi). If you alter scale after the normal bake, the color bake's patterns shift, but the normals stay "locked" to the old layout—resulting in a "mismatched skin" effect in Three.js (e.g., light bounces wrong, making quartz look unnatural).
    - Best Practice: Set all parameters (e.g., scale 5-15 for macro feel) before both bakes. If a bake looks off, note the good settings, revert chain, and rebake both maps with those values. This ensures consistency without extra work.
    - When It's Okay to Change: Only for tests—bake a quick low-res version (512x512) to iterate scale, then apply the final value to both full bakes. For non-procedural (PBR/image-based) minerals, this is less critical since no Voronoi.
  - If mismatches occur, compare PNGs side-by-side (e.g., in an image editor) or load in your app to spot issues early. Reference Step 7 in the guide for iteration tips!

**Quick Node Setup for Tileable Voronoi**
- I can't get the bake to look tileable for a procedural mineral? The bake has too many features (>8) but if I reduce the scaling it doesn't look tileable (If there's no noticeable mismatch, discontinuity, or hard line (the pattern flows naturally across boundaries), it's tileable.)
  - Here's the full node chain I recommend, step by step, assuming you're starting from a basic Principled BSDF material or the BlenderKit quartz procedural. This ensures periodicity for tileability while controlling feature count (aim for 4-6 cells via the initial scale). Connect them in sequence in the Shader Editor:

  - Texture Coordinate node (input): Use the "Generated" output for automatic 0-1 UV mapping on your baking plane. (This provides the base coordinates for the pattern.)
  - Mapping node (optional, but helpful for tweaks): Connect Texture Coordinate's Generated to this. Set Location/Rotation to 0, Scale to 1 initially. This lets you offset/rotate the pattern if needed without breaking periodicity.
  - Vector Math node (set to Scale): Connect the vector output from Texture Coordinate (or Mapping) here. Set the Scale value to a low number like 1.5-3 to control overall feature size—lower values mean larger cells/fewer features (targeting 4-6). Then multiply this scaled vector by 2π (use a Value node with 6.283) via another Vector Math (Multiply) to create the periodic wavelength. (This prepares for the circular mapping.)
  - Separate XYZ node: Connect the scaled/multiplied vector here to split into X, Y, Z components. (We'll use X and Y for 2D tiling; ignore or set Z to 0 for flat patterns.)
  - Math nodes for Sine and Cosine:
  - Connect X to a Math node set to Sine.
  - Connect Y to a Math node set to Cosine.
  - (For added variation in quartz veins, connect a offset version of X or Y to another Sine/Cosine for a Z or W component.)
![Optional chain configuration for procedural minerals](docs/tileable_math_example.png)
  - Combine XYZ node (or Combine XYZW for 4D): Recombine the Sine (X), Cosine (Y), and 0 or another trig function (Z). If using 4D Voronoi, add a W from another Sine on a phase-shifted coord (e.g., X+1).
  - Voronoi Texture node: Connect the combined vector to its Vector input. Set:
  - Dimension: 3D or 4D (4D adds smoothness and avoids repetition artifacts).
  - Feature: F1 or F2 (F2 for softer cells; mix with F1 via MixRGB if veins look too sharp).
  - Distance: Chebychev or Manhattan for angular quartz-like edges (avoid Euclidean for rounder blobs).
  - Scale: 1 (let the earlier Vector Math handle sizing).
  - Randomness: 0.2-0.4 for natural irregularity without chaos.
  - (If from BlenderKit, duplicate and insert this modified chain into the existing Voronoi's input to enhance it.)

  - ColorRamp or RGB Curves node (for color variation): Connect Voronoi's Color or Distance output here. Map the grayscale to quartz hues—e.g., white/grey for crystals, subtle blues/pinks for veins. Adjust stops for contrast (avoid flatness).
  - Emission shader (for color bake): Connect the ColorRamp output to Emission's Color input. Set Strength to 1. (This captures pure procedural colors without lighting interference.)
  - Material Output node: Connect Emission to the Surface input. (For normal baking, swap to a Normal Map node connected from Voronoi's Normal output, then to BSDF's Normal.)

  - To bake: Select your plane object, set Bake Type to Emit (for color) or Normals (for normals), choose a new Image node in the Image Editor as the target (e.g., 1024x1024 PNG), and hit Bake. The periodicity from the sine/cosine wrapping ensures the edges tile seamlessly—test by duplicating the baked PNG in an editor as I described before.


- if the boundaries are apparent it can still be called tileable if it looks somwhat natural? in the case of Quartz especially since the users will not be looking at a close up view of it?
  - for natural, organic textures like quartz in a game context (especially a voxel-based mining app where blocks are viewed from a distance or in clusters), tileability doesn't have to be perfectly seamless with zero visible boundaries to be "good enough." If the pattern repeats in a way that looks somewhat natural—meaning any subtle seams or repetitions blend into the overall irregularity without creating obvious artifacts like hard lines or unnatural mirroring—it can absolutely work. Quartz, in particular, often features crystalline veins or clusters that aren't perfectly uniform in real life, so a bit of apparent structure can even enhance realism as long as it doesn't scream "tiled texture" and disrupt immersion.
  - Key factors to consider for your use case:
    - Viewing distance and scale: At ~80px per voxel face and with users not zooming in super close (e.g., like in Minecraft-style gameplay), minor boundary hints will likely get softened by mipmapping, anti-aliasing, lighting/shadows, and the normal map's depth effects. Distant or angled views will hide imperfections better than a flat, close-up inspection.
    - Natural variation: If the seams appear as subtle shifts that mimic real mineral variations (e.g., a faint color gradient or vein continuation), it's fine. The goal is perceptual seamlessness, not pixel-perfect matching—especially since procedurals like Voronoi are meant to simulate randomness.
    - Testing in context: The real test isn't in Blender's Image Editor; bake it, import to Three.js, apply to a few voxel cubes in a grid, and view in your app under typical conditions (with lighting, camera distance, and any post-processing). If it looks cohesive without distracting repeats, call it tileable for practical purposes.
  - That said, if the boundaries are too apparent in your current bake (e.g., creating a grid-like repetition that feels artificial), it's worth tweaking to minimize them for polish. Based on the image you shared, which has those sharper, more geometric cells from Chebychev, it might emphasize boundaries more than needed for quartz. To get back closer to the "intended" quartz look (typically more fluid, veiny, and less blocky):
    - Switch the Voronoi Distance metric to Euclidean (for rounder, more organic cells) or Manhattan (for diagonal, vein-like edges that feel less rigid).
    - Lower Randomness further (e.g., 0.1-0.2) to soften the pattern without losing features.
    - Blend in a subtle Noise Texture (via MixRGB on the Voronoi output) to add irregularity and break up any repetitive feel—connect it to the ColorRamp input with a low factor (0.1-0.3) for quartz-like speckles or distortions.
  - If the sine/cosine periodic setup is still making it too uniform, increase the initial Scale slightly in the Vector Math node (e.g., to 3-4) while keeping feature count low, or add a small offset to the phase (e.g., add 0.5 to X before Sine).
  - Re-bake after changes, tile-test a 2x2 or 3x3 grid in an image editor, and iterate. If this node approach keeps falling short on the quartz aesthetic, consider layering a Musgrave Texture (ridged mode) over the Voronoi for more crystalline veins—it's often more tile-friendly out of the box and can be made periodic similarly.




If bakes underwhelm, try pre-made PNGs from ambientCG.
