<script>
    import {createEventDispatcher} from "svelte";
    import {fade} from 'svelte/transition';

    import {classicFont} from "../stores.js";
    
    const dispatch = createEventDispatcher();
    
    export let name;
    export let effects;
    export let description;
    export let cost;
    export let types = [];
    export let type = "";
    export let id;
    export let quantity = null;
    export let expansion = "";

    export let waitingForSelection;
    export let numSelected;
    export let selected = false;
    export let selectedAll;
    export let selectedCardIds = [];
    export let invalidCardNames = [];
    export let invalidCardIds = [];

    let hovering = false;
    let selectable = true;
    let selectionIndex = null;

    // Primordial types
    $: action = types.includes("action") && !types.includes("attack") && !types.includes("reaction");
    $: attack = types.includes("attack");
    $: reaction = types.includes("reaction");
    $: victory = types.includes("victory");
    $: curse = types.includes("curse");
    $: treasure = types.includes("treasure");
    $: basicTreasure = ["Copper", "Silver", "Gold", "Platinum"].includes(name);
    $: basicVictory = ["Curse", "Estate", "Duchy", "Province", "Colony"].includes(name);

    // Combined types
    $: victory_action = types.includes("victory") && types.includes("action");
    $: victory_treasure = types.includes("victory") && types.includes("treasure");
    $: treasure_reaction = types.includes("treasure") && types.includes("reaction");
    $: victory_reaction = types.includes("victory") && types.includes("reaction");

    // Bane "type"
    $: bane = types.includes("bane");

    function renderText(text) {
        return text
            .replaceAll("$", `<i class="fa-solid fa-coins"></i>`)
            .replaceAll("victory points", `<i class="bi bi-shield-shaded"></i>`)
            .replaceAll("victory point", `<i class="bi bi-shield-shaded"></i>`);
    }

    $: renderedEffects = effects.map(renderText);
    $: renderedDescription = description.map(renderText);

    $: {
        if (!waitingForSelection.value) {
            selectable = true;
        }
        else {
            selectable = (
                // Don't allow selection if this card is the wrong type
                (types.includes(waitingForSelection.type.toLowerCase()) || waitingForSelection.type == "")
                // Don't allow selection if the card costs more than the maximum cost
                && (waitingForSelection.maxCost == null || cost <= waitingForSelection.maxCost)
                // Don't allow selection if an exact cost is specified and the card doesn't have the exact cost
                && ((waitingForSelection.exactCost == false || cost == waitingForSelection.maxCost) || !("exactCost" in waitingForSelection) || waitingForSelection.exactCost == null)
                // Dont allow selection if the card is not in the supply
                && (quantity != 0)
                // Don't allow selection if the card is explicity disallowed (e.g., Contraband)
                && (!invalidCardNames.includes(name))
                && (!invalidCardIds.includes(id))
            );
        }
    }

    $: unselectable = !selectable || quantity == 0;

    function clicked() {
        if (
            !waitingForSelection.value 
            ||
            !selectable
            ||
            // Don't allow selection if the maximum number of cards is already selected (unselection is fine)
            (!selected && waitingForSelection.maxCards != null && numSelected >= waitingForSelection.maxCards)
        ) {
            return;
        }
        selected = !selected;
        dispatch(
            "clicked", 
            {
                name: name,
                effects: effects,
                description: description,
                cost: cost,
                type: type,
                id: id,
                selected: selected,
            }
        );
    }

    $: if (waitingForSelection != null && !waitingForSelection.value) {
        selected = false;
    }

    $: if (selectedAll) {
        if (waitingForSelection.value && type.toLowerCase().includes(waitingForSelection.type)) {
            if (!selected) {
                selected = true;
                dispatch(
                    "clicked", 
                    {
                        name: name,
                        effects: effects,
                        description: description,
                        cost: cost,
                        type: type,
                        id: id,
                        selected: selected,
                    }
                );
            }
        }
    }

    $: if (selected) {
        selectionIndex = selectedCardIds.indexOf(id) + 1;
    }
    else {
        selectionIndex = null;
    }
</script>

<main
    in:fade
    on:click={clicked}
    on:dblclick={
        () => {
            hovering = true;
        }
    }
    class:action
    class:attack
    class:reaction
    class:victory
    class:curse
    class:treasure
    class:basicTreasure
    class:basicVictory
    class:victory_action
    class:victory_treasure
    class:treasure_reaction
    class:victory_reaction
    class:bane
    class:unselectable
    class:selected
    class:classic={$classicFont}
>
    {#if quantity == null}
        <div class="name">{name}</div>
    {:else if quantity == "inf"}
        <div class="name">{name} &ndash &#8734;</div>
    {:else}
        <div class="name">{name} &ndash {quantity}</div>
    {/if}
    <span class="hoverable-text">
        <span class="hoverable-text-line">
            {expansion}
        </span>
    </span>
    {#if selectionIndex != null && waitingForSelection.ordered}
        <span class="selection-index">
            {selectionIndex}
        </span>
    {/if}
    <ul class="effects">
        {#each renderedEffects as effect}
            <li>{@html effect}</li>
        {/each}
    </ul>
    <ul class="description">
        {#each renderedDescription as description}
            <li>{@html description}</li>
        {/each}
    </ul>
    <div class="footer">
        <div class="cost">{cost}&nbsp;<i class="fa-solid fa-coins"></i></div>
        <div class="type">{type}</div>
    </div>
</main>

<style lang="scss">
    $ratio: 1.618;
    $width: 200px;
    $height: $width * $ratio;

    $padding: 10px;
    $padding-basis: 15px;
    $header-padding: 0px 0px $padding-basis 0px;
    $corner-radius: 20px;
    $margin: 5px;

    $shadow-color: rgba(127, 145, 163, 0.5);
    $shadow: 1px 1px 4px 4px $shadow-color;

    $font-size: 16px;
    $dark-text-color: #343338;
    $light-text-color: #dadada;
    $point: #100e17;
    $point-light: rgb(33, 29, 47);

    $dark-scrollbar-color: #34333880;
    $dark-scrollbar-color-hover: #343338;
    $light-scrollbar-color: #d9d9d980;
    $light-scrollbar-color-hover: #dadada;


    main {
        border: 1px solid slategrey;
        display: flex;
        flex: 0 0 auto;
        position: relative;
        width: $width;
        min-height: $height;
        max-height: $height;
        font-size: $font-size;
        color: $light-text-color;
        flex-direction: column;
        padding: $padding;
        margin-right: $margin;
        border-radius: $corner-radius;
        box-shadow: $shadow;
        transition: 0.4s ease-out;
        position: relative;
        left: 0px;
        right: 50px;
        overflow-y: hidden;
        overflow-x: hidden;
        font-family: "Segoe UI", sans-serif;

        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background-color: transparent;
        }
        ::-webkit-scrollbar-thumb {
            border-radius: 20px;
            border: 2px solid transparent;
            background-clip: content-box;
        }
    }

    main:hover {
        transform: translateY(-20px);
        transition: 0.4s ease-out;
        transition-delay: 0.1s;
    }

    main .hoverable-text {
        visibility: hidden;
        position: absolute;
        top: 0px;
        right: 0px;
        background-color: #343338;
        color: #dadada;
        font-size: 85%;
        border-radius: $corner-radius;
        border-color: #dadada;
        border-width: 1px;
        margin-top: $margin;
        margin-right: $margin;
        padding: 7px;
    }

    main:hover .hoverable-text {
        visibility: visible;
        transition-delay: 1s;
    }

    main .selection-index {
        position: absolute;
        bottom: 0%;
        left: 50%;
        transform: translate(-50%, 0);
        background-color: #343338;
        color: #dadada;
        font-size: 85%;
        border: 3px solid red;
        border-bottom: 0;
        border-top-left-radius: $corner-radius;
        border-top-right-radius: $corner-radius;
        padding: 7px;
        padding-left: 10px;
        padding-right: 10px;
    }

    .selected {
        border: 3px solid red;
        transform: translateY(-20px);
        transition: 0.4s ease-out;
    }

    .action {
        background-color: #343338;
        color: $light-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $light-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $light-scrollbar-color-hover;
        }
    }

    .action .hoverable-text, .action .selection-index {
        background-color: #dadada;
        color: #343338;
    }

    .attack {
        background-color: #ffcccc;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .attack .hoverable-text, .attack .selection-index {
        color: #ffcccc;
    }

    .reaction {
        background-color: #80bfff;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .reaction .hoverable-text, .reaction .selection-index {
        color: #80bfff;
    }

    .victory {
        background-color: #c1f0c1;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory .hoverable-text, .victory .selection-index {
        background-color: #343338;
        color: #c1f0c1;
    }

    .curse {
        background-color: #dab3ff;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .curse .hoverable-text, .curse .selection-index {
        color: #dab3ff;
    }

    .treasure {
        background-color: #fff0b3;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .treasure .hoverable-text, .treasure .selection-index {
        color: #fff0b3;
    }

    .basicTreasure .description {
        padding-top: 40px;
        font-size: 60px;
    }

    .basicVictory .description {
        padding-top: 40px;
        font-size: 60px;
    }

    .victory_action {
        background-color: #c1f0c1;
        background: repeating-linear-gradient(
            -45deg,
            #c1f0c1,
            #c1f0c1 30px,
            rgba(52, 51, 56, 0.05) 30px,
            rgba(52, 51, 56, 0.05) 60px,
        ), #c1f0c1;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory_action .hoverable-text, .treasure .selection-index {
        color: #c1f0c1;
    }

    .victory_treasure {
        background: repeating-linear-gradient(
            -45deg,
            #fff0b3,
            #fff0b3 30px,
            rgba(193, 240, 193, 0.2) 30px,
            rgba(193, 240, 193, 0.2) 60px,
        ), #fff0b3;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory_treasure .hoverable-text, .treasure .selection-index {
        color: #fff0b3;
    }

    .treasure_reaction {
        background: repeating-linear-gradient(
            -45deg,
            #fff0b3,
            #fff0b3 30px,
            rgba(128, 191, 255, 0.1) 30px,
            rgba(128, 191, 255, 0.1) 60px,
        ), #fff0b3;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .treasure_reaction .hoverable-text, .treasure .selection-index {
        color: #fff0b3;
    }

    .victory_reaction {
        background-color: #c1f0c1;
        background: repeating-linear-gradient(
            -45deg,
            #c1f0c1,
            #c1f0c1 30px,
            rgba(128, 191, 255, 0.1) 30px,
            rgba(128, 191, 255, 0.1) 60px,
        ), #c1f0c1;
        color: $dark-text-color;

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory_reaction .hoverable-text, .treasure .selection-index {
        color: #c1f0c1;
    }

    .bane {
        box-shadow: $shadow, inset 0 0 15px #80bfff;
    }

    .name {
        display: flex;
        justify-content: space-between;
        width: $width;
        padding: $header-padding;
    }

    .classic .name {
        font-family: trajan-pro-3, serif;
    }

    .effects {
        font-weight: 700;
        font-style: normal;
        list-style-type: none;
        padding: 0;
        margin-bottom: $padding-basis;
        margin-left: 0;
        font-family: serif;
    }

    .classic .effects {
        font-family: minion-pro, serif;
    }

    .description {
        font-weight: 400;
        font-style: normal;
        list-style-type: none;
        padding: 0;
        margin-left: 0;
        margin-bottom: $padding-basis;
        overflow-y: auto;
        font-family: serif;
    }

    .classic .description {
        font-family: minion-pro, serif;
    }

    .description li:not(:last-child) { 
        margin-bottom: 10px;  
    }

    .footer {
        display: flex;
        justify-content: space-between;
        position: absolute;
        width: $width;
        bottom: $margin;
        margin-top: $padding-basis;
        padding-right: $padding-basis + 4px;
    }

    .classic .footer {
        font-family: trajan-pro-3, serif;
    }

    .unselectable {
        opacity: 0.5;
        box-shadow: none;
        top: 1px;
        left: 1px;
    }
</style>