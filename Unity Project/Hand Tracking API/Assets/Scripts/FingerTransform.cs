using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FingerTransform : MonoBehaviour
{
    [SerializeField] Transform Target;

    // Start is called before the first frame update
    void Start()
    {
        //Target = Where the data is being stored
        Debug.Log(gameObject.name);
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = Target.position;
    }
}
