import {Composition} from "remotion";
import {compositionRegistry} from "./compositions/registry";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {compositionRegistry.map((definition) => (
        <Composition key={definition.id} {...definition} />
      ))}
    </>
  );
};
