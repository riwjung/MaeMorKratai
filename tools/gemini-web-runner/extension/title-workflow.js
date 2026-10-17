/* Shared title contract. Imported artwork stays in this tab's memory. */
(() => {
 'use strict';
 const spec = `TITLE SYSTEM — MMKT TITLE V1
Print exactly the CARD TITLE below, once, in English UPPERCASE. No other text, numbers, signature or watermark.
Use a clean, narrow, gently rounded sans-serif, medium weight, upright, ivory #FFF4E4. No shadow, outline, swash or decorative initials.
Use the SAME lettering size on ALL 78 cards: capital-letter height 2.4% of total canvas height (about 63 px at 2624 px high). Fixed tracking 0.08 times the capital height. Never enlarge short titles or shrink long ones.
One horizontal line centered at x=50%, with its baseline at y=92% of the full canvas. Keep the title within x=12%–88%, in the quiet bottom band. Even the longest card title must fit at this same size. No wrapping, stretching or extra plaque.
Match the approved typography reference's actual letterforms, weight, size RELATIVE TO CANVAS, spacing, color and baseline. Replace its words with this card's exact title; do not copy its scene or title. If no approved reference is attached, create ONE candidate using this specification for owner review.`;
 const quality = `COMPLETENESS CHECK BEFORE RETURNING THE IMAGE
Keep one complete, continuous ivory rounded rectangle visible on all four sides, including both bottom corners and the bottom edge beneath the title. Never erase the lower border with a solid title band. Keep the entire border inside the canvas with a consistent safe margin; no cropped or open frame.
The rabbit has two eyes. If eyebrows are drawn on a visible front-facing face, draw a matching pair; never leave a single isolated eyebrow. If the original mascot has no eyebrows, do not invent a lone eyebrow. Preserve the simple original rabbit identity, ears, paws and suit-symbol counts.
Check the complete border, face, exact English card name and consistent lettering before returning one image. This instruction is not proof that the result passed human review.`;
 const normalize = name => name.replace(/\.[^.]+$/, '').replace(/^\d{2}[-_ ]/, '').trim().toLowerCase().replace(/[ _]+/g, '-');
 function cardForFile(name, deck) {
  const id=normalize(name);
  return deck.find(c=>c.id===id||normalize(c.name)===id)||null;
 }
 function prompt(card, {mode, approved, sourceName, repair}) {
  if(mode==='legacy')return card.legacyPrompt;
  if(mode==='repair'){
   if(!repair||!['frame','brows','both','custom'].includes(repair.issue))throw Error('เลือกจุดแก้ก่อนซ่อมภาพ');
   const fixes=[];
   if(['frame','both'].includes(repair.issue))fixes.push('Repair ONLY the broken/incomplete ivory rounded frame: connect both side edges to both lower rounded corners and restore the complete bottom edge underneath the existing title. Match existing line thickness, ivory color and inset. Keep all four sides fully on canvas. Do not cover the title, move the rabbit, repaint the landscape, or add a second frame.');
   if(['brows','both'].includes(repair.issue))fixes.push('Repair the one-sided eyebrow on the main rabbit: preserve the existing eyebrow and add its missing matching counterpart above the other visible eye, matching stroke weight, color, length and expression. Do not change the eyes, nose, mouth, cheeks, ears or pose. If a balanced pair already exists, preserve it.');
   if(repair.notes)fixes.push('Owner correction notes: '+repair.notes);
   return `REPAIR EXISTING APPROVED ART — LOCAL CORRECTIONS ONLY
ATTACHMENT ROLES:
${sourceName} = TARGET ARTWORK TO REPAIR. Use this exact existing card as the edit base, not as inspiration for a new scene.
IMG_5392.JPG = original mascot/art style reference; do not replace the target composition with its pose.
${approved?'MMKT_APPROVED_TITLE_REF = optional typography reference. Preserve the target title unless owner notes explicitly request a typography correction.':'No extra typography reference is required: preserve the target artwork’s existing title and lettering.'}

${fixes.join('\n')}

Preserve the original aspect ratio, dimensions, composition, illustration style, colors, lighting, characters, pose, props and all details outside the specified repairs. Do not regenerate an alternative scene. Do not add or remove suit symbols. Preserve the existing English title exactly, with its current letterforms, size, spacing and location; do not redraw or duplicate the title. No additional text, logos or watermarks.
CARD SCENE: ${card.name.toUpperCase()}
CARD TITLE: ${card.name.toUpperCase()}
Return one repaired image. Inspect the requested corrections before returning it; preserve everything else.`;
  }
  const roles=['ATTACHMENT ROLES (use filenames, not upload order):',
   'IMG_5392.JPG = original mascot and art-style reference. Keep this deck’s original 2D drawing style.',
   approved?'MMKT_APPROVED_TITLE_REF = owner-approved first titled card. Typography reference ONLY; never copy its card identity or scene.':'No approved typography reference yet: this is a single candidate for review.'];
  if(mode==='edit') roles.push(`${sourceName} = TARGET ORIGINAL ARTWORK. Edit THIS image, preserving the original dimensions, composition, rabbit, palette, frame, pose and all symbols. Add only the requested title to its bottom quiet band. Do not redraw, crop, replace the scene, or change the card identity. If the band has insufficient space, do not move artwork or cover important symbols; explain the conflict instead of redesigning the card.`);
  if(mode==='edit')return `${roles.join('\n')}\n\nEDIT EXISTING ARTWORK — ADD TITLE ONLY\n\n${spec}\n\nCARD SCENE: ${card.name.toUpperCase()}\nCARD TITLE: ${card.name.toUpperCase()}\nReturn one edited image of the TARGET ORIGINAL ARTWORK. The scene is already complete; preserve it.`;
  return `${roles.join('\n')}\n\n${card.prompt}`;
 }
 globalThis.MMKT_TITLES={spec,quality,cardForFile,prompt};
})();
