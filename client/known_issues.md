1. Sentry with both cards returning to deck is somehow causing duplicates to attempt to show up in one carousel (presumably Hand). This has been observed during the "choose_treasures_from_hand" interaction.

    ````
    Uncaught (in promise) Error: Cannot have duplicate keys in a keyed each
        at validate_each_keys (index.mjs:1551:19)
        at Object.update [as p] (card_carousel.svelte:180:27)
        at update (index.mjs:1085:36)
        at flush (index.mjs:1052:13)
    ````

2. It is still possible to buy the named card when a Loan is played. The entire server-side of these interactions should probably be tightened up.

3. Card carousels are not always updated when they should be. The server should send updates whenever something changes. Maybe add getters and setters to the supply, etc. to handle this.