<script>
    import {createEventDispatcher} from "svelte";
    import {fade} from 'svelte/transition';
    
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
    export let forceBane = false;

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
    $: bane = types.includes("bane") || forceBane;

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
>
    <div class="header">
        <div class="name">
            {name}
        </div>
        {#if quantity == "inf"}
            <div class="quantity">
                &#8734
            </div>
        {:else if quantity}
            <div class="quantity">
                {quantity}
            </div>
        {/if}
    </div>
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
    <div class="body">
        {#if renderedEffects.length > 0}
            <ul class="effects">
                {#each renderedEffects as effect}
                    <li>{@html effect}</li>
                {/each}
            </ul>
        {/if}
        <ul class="description">
            {#each renderedDescription as description}
                <li>{@html description}</li>
            {/each}
        </ul>
    </div>
    <div class="footer">
        <div class="cost">{cost}&nbsp;<i class="fa-solid fa-coins"></i></div>
        {#if forceBane}
            <div class="type">Bane, {type}</div>
        {:else}
            <div class="type">{type}</div>
        {/if}
    </div>
</main>

<style lang="scss">
    $margin: 5px;

    $dark-scrollbar-color: #34333880;
    $dark-scrollbar-color-hover: var(--action-card-color);
    $light-scrollbar-color: #d9d9d980;
    $light-scrollbar-color-hover: #dadada;

    main {
        border: var(--card-border);
        display: flex;
        flex: 0 0 auto;
        width: var(--card-width);
        min-height: calc(var(--card-width) * 1.618);
        max-height: calc(var(--card-width) * 1.618);
        font-size: var(--card-font-size);
        flex-direction: column;
        padding: var(--card-padding);
        margin-right: $margin;
        border-radius: var(--card-border-radius);
        box-shadow: 1px 1px 4px 4px var(--card-shadow-color);
        transition: 0.4s ease-out;
        position: relative;
        left: 0px;
        right: 50px;
        overflow-y: hidden;
        overflow-x: hidden;

        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background-color: transparent;
        }
        ::-webkit-scrollbar-thumb {
            border-radius: var(--card-border-radius);
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
        background-color: var(--action-card-color);
        color: var(--light-text-color);
        font-size: 85%;
        border-radius: var(--card-border-radius);
        border-color: var(--border-color);
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
        background-color: var(--action-card-color);
        color: #dadada;
        font-size: 85%;
        border: var(--selected-card-border);
        border-bottom: 0;
        border-top-left-radius: var(--card-border-radius);
        border-top-right-radius: var(--card-border-radius);
        padding: 7px;
        padding-left: 10px;
        padding-right: 10px;
    }

    .selected {
        border: var(--selected-card-border);
        transform: translateY(-20px);
        transition: 0.4s ease-out;
    }

    .action {
        background-color: var(--action-card-color);
        color: var(--light-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $light-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $light-scrollbar-color-hover;
        }
    }

    .action .hoverable-text, .action .selection-index {
        background-color: var(--light-text-color);
        color: var(--action-card-color);
    }

    .attack {
        background-color: var(--attack-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .attack .hoverable-text, .attack .selection-index {
        color: var(--attack-card-color);
    }

    .reaction {
        background-color: var(--reaction-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .reaction .hoverable-text, .reaction .selection-index {
        color: var(--reaction-card-color);
    }

    .victory {
        background-color: var(--victory-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory .hoverable-text, .victory .selection-index {
        background-color: var(--action-card-color);
        color: var(--victory-card-color);
    }

    .curse {
        background-color: var(--curse-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .curse .hoverable-text, .curse .selection-index {
        color: var(--curse-card-color);
    }

    .treasure {
        background-color: var(--treasure-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .treasure .hoverable-text, .treasure .selection-index {
        color: var(--treasure-card-color);
    }

    .victory_action {
        background-color: var(--victory-card-color);
        background: repeating-linear-gradient(
            -45deg,
            var(--victory-card-color),
            var(--victory-card-color) var(--card-stripe-width),
            color-mix(in srgb, var(--victory-card-color), var(--action-card-color) 5%) var(--card-stripe-width),
            color-mix(in srgb, var(--victory-card-color), var(--action-card-color) 5%) calc(2 * var(--card-stripe-width)),
        ), var(--victory-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory_action .hoverable-text, .treasure .selection-index {
        color: var(--victory-card-color);
    }

    .victory_treasure {
        background: repeating-linear-gradient(
            -45deg,
            var(--treasure-card-color),
            var(--treasure-card-color) var(--card-stripe-width),
            color-mix(in srgb, var(--treasure-card-color), var(--victory-card-color) 30%) var(--card-stripe-width),
            color-mix(in srgb, var(--treasure-card-color), var(--victory-card-color) 23%) calc(2 * var(--card-stripe-width)),
        ), var(--treasure-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory_treasure .hoverable-text, .treasure .selection-index {
        color: var(--treasure-card-color);
    }

    .treasure_reaction {
        background: repeating-linear-gradient(
            -45deg,
            var(--treasure-card-color),
            var(--treasure-card-color) var(--card-stripe-width),
            color-mix(in srgb, var(--treasure-card-color), var(--reaction-card-color) 12%) var(--card-stripe-width),
            color-mix(in srgb, var(--treasure-card-color), var(--reaction-card-color) 12%) calc(2 * var(--card-stripe-width)),
        ), var(--treasure-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .treasure_reaction .hoverable-text, .treasure .selection-index {
        color: var(--treasure-card-color);
    }

    .victory_reaction {
        background-color: var(--victory-card-color);
        background: repeating-linear-gradient(
            -45deg,
            var(--victory-card-color),
            var(--victory-card-color) var(--card-stripe-width),
            color-mix(in srgb, var(--victory-card-color), var(--reaction-card-color) 15%) var(--card-stripe-width),
            color-mix(in srgb, var(--victory-card-color), var(--reaction-card-color) 15%) calc(2 * var(--card-stripe-width)),
        ), var(--victory-card-color);
        color: var(--dark-text-color);

        ::-webkit-scrollbar-thumb {
            background-color: $dark-scrollbar-color;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: $dark-scrollbar-color-hover;
        }
    }

    .victory_reaction .hoverable-text, .treasure .selection-index {
        color: var(--victory-card-color);
    }

    .action.bane {
        color: color-mix(in srgb, var(--light-text-color), var(--curse-card-color) 70%);
    }

    :not(.action).bane {
        color: color-mix(in srgb, var(--dark-text-color), var(--curse-card-color) 40%);
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        position: relative;
        width: calc(var(--card-width) - 2 * var(--card-padding));
        gap: 5px;
        top: -$margin;
        font-family: var(--title-font-family);
    }

    .name {
        display: flex;
        justify-content: space-between;
        width: var(--card-width);
        text-wrap: nowrap;
        overflow-x: auto;
        scrollbar-width: none;
    }

    .name::-webkit-scrollbar {
        display: none;
    }

    .quantity {
        text-wrap: nowrap;
    }

    .body {
        display: flex;
        flex: 1;
        flex-direction: column;
        position: relative;
        overflow-y: auto;
        padding-top: var(--card-body-top-padding);
        font-family: var(--card-body-font-family);
    }

    .effects {
        font-weight: 700;
        font-style: normal;
        list-style-type: none;
        padding: 0;
        margin-left: 0;
    }

    .description {
        display: flex;
        flex-direction: column;
        gap: 10px;
        font-weight: 400;
        font-style: normal;
        list-style-type: none;
        padding: 0;
        margin-left: 0;
        margin-bottom: 0;
    }

    .basicTreasure .description, .basicVictory .description {
        font-size: 350%;
        height: 100%;
        justify-content: space-evenly;
        margin-top: calc(-1 * var(--card-body-top-padding));
    }

    .footer {
        display: flex;
        flex: 0;
        justify-content: space-between;
        align-items: flex-end;
        position: relative;
        width: calc(var(--card-width) - 2 * var(--card-padding));
        bottom: -$margin;
        gap: 5px;
        font-family: var(--title-font-family);
    }

    .cost {
        text-wrap: nowrap;
    }

    .type {
        text-wrap: nowrap;
        overflow-x: auto;
        scrollbar-width: none;
    }

    .type::-webkit-scrollbar {
        display: none;
    }

    .unselectable {
        opacity: var(--unselectable-card-opacity);
        box-shadow: none;
        top: 1px;
        left: 1px;
    }
</style>