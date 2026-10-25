import { useState } from "react";


function ResearchForm({
    onResearch,
    loading
}) {

    const [topic, setTopic] = useState("");

    const [maxRevisions, setMaxRevisions] =
        useState(2);


    function handleSubmit(event) {

        event.preventDefault();

        if (!topic.trim()) {
            return;
        }

        onResearch(
            topic,
            maxRevisions
        );
    }


    return (

        <form
            className="research-form"
            onSubmit={handleSubmit}
        >

            <label>
                Research Topic
            </label>

            <textarea
                value={topic}
                onChange={(event) =>
                    setTopic(
                        event.target.value
                    )
                }
                placeholder={
                    "Example: Impact of generative AI on software development"
                }
                rows={5}
            />


            <label>
                Maximum Revisions
            </label>

            <select
                value={maxRevisions}
                onChange={(event) =>
                    setMaxRevisions(
                        Number(event.target.value)
                    )
                }
            >

                <option value={0}>
                    0
                </option>

                <option value={1}>
                    1
                </option>

                <option value={2}>
                    2
                </option>

                <option value={3}>
                    3
                </option>

            </select>


            <button
                type="submit"
                disabled={loading}
            >

                {loading
                    ? "Researching..."
                    : "Start Research"
                }

            </button>

        </form>
    );
}


export default ResearchForm;