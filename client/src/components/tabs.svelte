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
        flex-wrap: wrap;
        list-style-type: none;
        margin: 0;
        padding: 0;
        border-bottom: 1px solid #343338;
        text-align: center;
        justify-content: center;
    }

    span {
        border: 1px solid transparent;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        display: block;
        padding: 10px;
        cursor: pointer;
        margin-bottom: -1px;
        border-bottom: 1px solid #343338;
    }

    li:hover:not(.selected) > span {
        border-top-color: rgba(52, 51, 56, 0.2);
        border-left-color: rgba(52, 51, 56, 0.2);
        border-right-color: rgba(52, 51, 56, 0.2);
        background-color: rgba(128, 191, 255, 0.2);

    }

    li.selected > span {
        border-top-color: #343338;
        border-left-color: #343338;
        border-right-color: #343338;
        background-color: #80bfff;
    }
</style>