<script>
    import {onMount} from "svelte";

    export let tabNames = [];
    export let selectedTab = null;

    onMount(
        () => {
            if (tabNames.length > 0) {
                selectedTab = tabNames[0];
            }
        }
    );
</script>

<main>
    <ul>
        {#if tabNames.length > 0}
            {#each tabNames as tabName}
                <li class={selectedTab == tabName ? "selected" : ""}>
                    <span on:click={() => selectedTab = tabName}>
                        {tabName}
                    </span>
                </li>
            {/each}
        {/if}
    </ul>
</main>

<style>
    ul {
        display: flex;
        flex-wrap: nowrap;
        list-style-type: none;
        margin: 0;
        padding: 0;
        border-bottom: 1px solid var(--border-color);
        text-align: center;
        justify-content: center;
    }

    span {
        border: 1px solid transparent;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
        display: block;
        padding: 10px;
        cursor: pointer;
    }

    li:hover:not(.selected) > span {
        border-top-color: color-mix(in srgb, var(--body-background-color), var(--border-color) 20%);
        border-left-color: color-mix(in srgb, var(--body-background-color), var(--border-color) 20%);
        border-right-color: color-mix(in srgb, var(--body-background-color), var(--border-color) 20%);
        background-color: color-mix(in srgb, var(--body-background-color), var(--blue-color) 20%);
    }

    li.selected > span {
        border-top-color: var(--border-color);
        border-left-color: var(--border-color);
        border-right-color: var(--border-color);
        background-color: var(--blue-color);
        color: var(--dark-text-color);
    }
</style>